#!/usr/bin/env python
import os
import time
import _thread
import requests
import json
import configparser

from PIL import Image
from PIL import ImageDraw
from datetime import datetime

from rgbmatrix import graphics
from controller.matrix import MatrixController
from controller.mqttcontroller import MqttController
from controller.musicHandler import MusicHandler
from controller.notificationHandler import NotificationHandler
from controller.weather import Weather
from controller.gif_slicer import GifSlicer
from controller.artNet import ArtNet
from controller.textScroller import TextScroller
from controller.playlist import Playlist

########
#
# Screens
#
# 0 - News and Weather
# 1 - Music or Screen 0
# 2 - GIFs
# 3 - Images
# 4 - Artnet
# 5 - Sprittpreise
#
# 100 - enable Playlist (over MQTT)
#
########


class InfoDisplay:
    __config = configparser.ConfigParser()
    __currentSong = 'Hier koennte Ihre Werbung stehen.   '
    __weatherTemp = None
    __brightness = 50   # brightness is set in from 0% - 100%
    __global_font_color = (255, 255, 255)
    __screen = 1
    __power = True
    __playlistEnabled = False

    def __init__(self, config, matrix_controller: MatrixController):
        self.__config = config
        self.display = matrix_controller

        self.__screen = self.__config["Misc"]["startScreen"]
        self.__plaxlistEnabled = self.__config["Misc"]["autoPlaylist"]


        _thread.start_new_thread(self.__render_loop, ())

        self.weather = Weather()
        self.weather.image_path = os.path.dirname(os.path.realpath(__file__)) + '/../assets/weather/'
        self.music = MusicHandler()
        self.music.image_path = os.path.dirname(os.path.realpath(__file__)) + '/../assets/cover.jpg'
        self.notificationHandler = NotificationHandler(self.__load_font('6x10.bdf'),self.display.canvas)
        self.gifSlicer = GifSlicer()
        self.gifSlicer.cacheFolder = os.path.dirname(os.path.realpath(__file__)) + '/../assets/gifs/tmp'

        self.newsText = TextScroller(self.__load_font('5x7.bdf'))
        self.songTitle = TextScroller(self.__load_font('6x10.bdf'))
        self.sprittpreiseText = TextScroller(self.__load_font('5x7.bdf'))

        self.playlist = Playlist(10,[1,5])

        if(self.__config["ArtNet"]["enabled"]):
            self.dmx = ArtNet(universe=self.__config["ArtNet"]["universe"])
            self.dmx.addLight(1, 0, 0, 64, 32)

        mqtt = MqttController(self.__config["MQTT"]["host"], int(self.__config["MQTT"]["port"]))
        mqtt.subscribe_to_topic('smarthome/display/screen', self.__callback_set_screen)
        mqtt.subscribe_to_topic('smarthome/display/cmnd', self.__callback_set_cmnd)
        mqtt.subscribe_to_topic('smarthome/display/play_gif', self.__callback_play_gif)
        mqtt.subscribe_to_topic('smarthome/display/show_img', self.__callback_show_img)
        mqtt.subscribe_to_topic('smarthome/display/notification', self.notificationHandler.callback_handle_msg)
        mqtt.subscribe_to_topic('weather', self.weather.parseData)
        mqtt.subscribe_to_topic('newsticker/ntv', self.__callback_newsHandler)
        mqtt.subscribe_to_topic('smarthome/sonos/wohnzimmer', self.music.parseMsg)
        mqtt.subscribe_to_topic('stats/sprittpreise', self.__callback_sprittpreise)

    @staticmethod
    def __load_font(filename):
        font = graphics.Font()
        font.LoadFont(os.path.dirname(os.path.realpath(__file__)) + '/../fonts/' + filename)
        return font

    def __callback_set_screen(self, msg):
        try:
            target = int(msg.decode('UTF-8'))

            if (target == 100):
                self.__playlistEnabled = True
            else:
                self.__playlistEnabled = False

            self.__screen = target
        except:
            self.__screen = 0

    def __callback_set_cmnd(self, msg):
        data = json.loads(msg.decode('UTF-8'))
        color = data.get("color", None)
        brightness = data.get("brightness", None)
        power = data.get("power", None)
        if(color):
            self.__global_font_color = (color[0], color[1], color[2])

        if(brightness):
            self.__brightness = brightness

        if(power != None):
            self.__power = power

    def __callback_play_gif(self, msg):
        data = json.loads(msg.decode('UTF-8'))
        path = data.get("path")
        if(path):
            if(self.gifSlicer.loadGif(path) > 0):
                self.__screen = 2
            else:
                self.__screen = 1

    def __callback_sprittpreise(self, msg):
        try:
            data = json.loads(msg.decode('UTF-8'))
            text_buffer = 'E10: %1.2f€   ' % data["e10"]
            text_buffer += 'Diesel: %1.2f€' % data["diesel"]
            self.sprittpreiseText.setText(text_buffer)
        except Exception as e:
            print("Sprittpreis Error:")
            print(e)

    def __callback_show_img(self, msg):
        data = json.loads(msg.decode('UTF-8'))
        path = data.get("path")
        if(path):
            try:
                image = Image.open(path)
                image = image.convert('RGB')
                image.thumbnail((64,32),Image.ANTIALIAS)
                self.__img = image
                self.__screen = 3

            except Exception as e:
                print(e)
                self.__screen = 1


    def __callback_getWeather(self, msg):
        weather = json.loads(msg.decode('UTF-8'))
        self.__weatherTemp = float(weather["tempc"])

    def __callback_newsHandler(self, msg):
        try:
            articles = json.loads(msg.decode('UTF-8'))
            text_buffer = " <-> "
            for post in articles:
                text_buffer += post["title"][0] + " <-> "
            self.newsText.setText(text_buffer)
        except Exception as e:
            print(e)

    def __render_loop(self):
        print('Render thread is running.')
        font_big = self.__load_font('8x13B.bdf')
        font_medium = self.__load_font('6x10.bdf')
        font_small = self.__load_font('5x7.bdf')

        marquee_songInfo_pos = self.display.canvas.width


        self.gifSlicer.loadGif(os.path.dirname(os.path.realpath(__file__)) + '/../assets/gifs/hamster.gif')

        while True:
            self.display.canvas.Clear()
            self.display.canvas.brightness = self.__brightness
            text_color = graphics.Color(self.__global_font_color[0], self.__global_font_color[1],
                                        self.__global_font_color[2])
            if self.__power:
                if(self.__playlistEnabled):
                    self.__screen = self.playlist.getScreen()

                # First check for Notification
                if(self.notificationHandler.notification):
                    self.__render_time(font_big, text_color)
                    self.notificationHandler.renderNotification(self.display.canvas)

                # Sprittpreise
                elif(self.__screen == 5):
                    self.__render_time(font_big, text_color)
                    self.sprittpreiseText.renderText(self.display.canvas, y=20 , color=[255,255,0])
                    self.newsText.renderText(self.display.canvas, y=30, color=[255,0,0])

                # Screen 4 ArtNet
                elif((self.__screen == 4) and self.__config["ArtNet"]["enabled"]):
                    self.dmx.createImage()
                    self.display.canvas.SetImage(self.dmx.image, unsafe=False)

                # Screen 3 Render Image
                elif(self.__screen == 3):
                    try:
                        self.display.canvas.SetImage(self.__img, unsafe=False)
                    except Exception as e:
                        print(e)


                # Screen 2 GIF
                elif(self.__screen == 2):
                    if(self.gifSlicer.nImages >= 1):
                        self.display.canvas.SetImage(self.gifSlicer.getImage(), unsafe=False)

                # Screen 1 and 0 Default
                else:
                    if(self.music.state == "playing")and(self.music.title)and(self.__screen == 1):
                        self.songTitle.setText(self.music.title)
                        self.songTitle.renderText(self.display.canvas, 29, color=[255,255,255])
                        marquee_songInfo_pos = self.__render_marquee_songInfo(font_small, marquee_songInfo_pos, graphics.Color(255,255,25))
                        self.__render_cover()
                        self.__render_song_pos(text_color)

                    else:
                        self.__render_time(font_big, text_color)
                        self.__render_weather(font_small, graphics.Color(255,255,0))
                        self.newsText.renderText(self.display.canvas, y=30, color=[255,0,0])

            self.display.canvas = self.display.matrix.SwapOnVSync(self.display.canvas)
            time.sleep(0.03)

    def __reader_gif_frame(self, delay, gif, gif_counter, size = [32,32]):
        if delay == 1:
            delay = 0
            if gif_counter == gif.numFrames:
                gif_counter = 1
            else:
                gif_counter += 1
        else:
            delay += 1

        frame = gif.get_frame(gif_counter)
        for x in range(1, size[0]):
            for y in range(1, size[1]):
                r, g, b = gif.get_pixel(x, y, frame)

                self.display.canvas.SetPixel(x , y , int(r * (self.__global_font_color[0] / 255)),
                                             int(g * (self.__global_font_color[1] / 255)),
                                             int(b * (self.__global_font_color[2] / 255)))

        return delay, gif_counter


    def __render_marquee_songInfo(self, font_small, marqueetext_pos, text_color):
        text_length = 1
        if(self.music.artist):
            text_length = graphics.DrawText(self.display.canvas, font_small, marqueetext_pos, 8, text_color,
                                        self.music.artist)
        if(self.music.artist):
            text_length_b = graphics.DrawText(self.display.canvas, font_small, marqueetext_pos, 18, text_color,
                                        self.music.album)
            if(text_length_b > text_length):
                text_length = text_length_b

        marqueetext_pos -= 0.5
        if marqueetext_pos + text_length < 21:
            marqueetext_pos = self.display.canvas.width

        return marqueetext_pos


    def __render_weather(self, font_small, text_color):
        weather_string = '%4.1f°C' % self.weather.temp
        graphics.DrawText(self.display.canvas, font_small, 31, 20, text_color, weather_string)
        self.display.canvas.SetImage(self.weather.icon, offset_x = 5, offset_y = 12, unsafe=False)


    def __render_time(self, font_big, text_color):
        time_string = time.strftime('%H:%M:%S')
        graphics.DrawText(self.display.canvas, font_big, 0, 11, text_color, time_string)
        #date_string = time.strftime('%d/%m')
        #graphics.DrawText(self.display.canvas, font_small, 0, 20, text_color, date_string)

    def __render_cover(self):
        self.display.canvas.SetImage(self.music.cover, unsafe=False)

    def __render_song_pos(self, color):
        #graphics.DrawLine(self.display.canvas, 0, 29, 63, 29, color)
        try:
            pos_track = datetime.now().timestamp() - self.music.start
            pos = int((pos_track / self.music.duration)* 63)
        except:
            pos = 0

        graphics.DrawLine(self.display.canvas, 0, 31, pos, 31, graphics.Color(0,0,255))
        #self.display.canvas.SetPixel(pos, 31, 0,255,255)


    def set_marquee_text(self, text):
        self.__marqueeText = text
