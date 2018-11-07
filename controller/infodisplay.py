#!/usr/bin/env python
import os
import time
import _thread
import requests

from rgbmatrix import graphics
from controller.matrix import MatrixController
from controller.gifparser import GifParser
from controller.mqttcontroller import MqttController


class InfoDisplay:
    __marqueeText = ''
    __currentSong = 'Hier könnte Ihre Werbung stehen.   '
    __weatherTemp = None

    __global_font_color = (10, 10, 10)

    def __init__(self, matrix_controller: MatrixController):
        self.display = matrix_controller
        _thread.start_new_thread(self.__render_loop, ())
        _thread.start_new_thread(self.__external_data_fetcher, ())

        mqtt = MqttController()
        mqtt.subscribe_to_topic('smarthome/haus/niklas/og/schlafzimmer/licht/rgb-display/color',
                                self.__callback_set_font_color)
        print('Render thread is running.')

    @staticmethod
    def __load_font(filename):
        font = graphics.Font()
        font.LoadFont(os.path.dirname(os.path.realpath(__file__)) + '/../fonts/' + filename)
        return font

    def __callback_set_font_color(self, msg):
        values = msg.decode('UTF-8').split(";")
        if len(values) == 3:
            col_red = int(float(values[0]))
            col_green = int(float(values[1]))
            col_blue = int(float(values[2]))
            self.__global_font_color = (col_red * 255 / 4096, col_green * 255 / 4096, col_blue * 255 / 4096)

    def __external_data_fetcher(self):
        while True:
            try:
                r = requests.get('http://192.168.178.34/hz/live_txt.php')
                r1 = requests.get('http://192.168.178.31:8080/rest/items/SqueezeliteNiklasWohnzimmer_Artist')
                r2 = requests.get('http://192.168.178.31:8080/rest/items/SqueezeliteNiklasWohnzimmer_Title')

                self.__weatherTemp = float(r.text.split('\n')[5])
                self.__currentSong = r1.json()['state'] + ' - ' + r2.json()['state']

                time.sleep(5)
            except requests.exceptions.RequestException:
                pass

    def __render_loop(self):
        font_big = self.__load_font('8x13B.bdf')
        font_small = self.__load_font('5x7.bdf')

        marqueetext_pos = self.display.canvas.width

        gif = GifParser(os.path.dirname(os.path.realpath(__file__)) + '/../assets/eq.gif')
        gif_counter = 0
        gif_delay = 0

        while True:
            self.display.canvas.Clear()

            text_color = graphics.Color(self.__global_font_color[0], self.__global_font_color[1],
                                        self.__global_font_color[2])

            self.__render_date_and_time(font_big, font_small, text_color)
            self.__render_weather(font_small, text_color)
            marqueetext_pos = self.__render_marquee_text(font_small, marqueetext_pos, text_color)
            gif_delay, gif_counter = self.__reader_gif_frame(gif_delay, gif, gif_counter)

            self.display.canvas = self.display.matrix.SwapOnVSync(self.display.canvas)
            time.sleep(0.03)

    def __reader_gif_frame(self, delay, gif, gif_counter):
        if delay == 1:
            delay = 0
            if gif_counter == gif.numFrames:
                gif_counter = 1
            else:
                gif_counter += 1
        else:
            delay += 1

        frame = gif.get_frame(gif_counter)
        for x in range(1, 12):
            for y in range(1, 12):
                r, g, b = gif.get_pixel(x, y, frame)

                self.display.canvas.SetPixel(x - 1, y + 20, int(r * (self.__global_font_color[0] / 255)),
                                             int(g * (self.__global_font_color[1] / 255)),
                                             int(b * (self.__global_font_color[2] / 255)))

        return delay, gif_counter

    def __render_marquee_text(self, font_small, marqueetext_pos, text_color):
        text_length = graphics.DrawText(self.display.canvas, font_small, marqueetext_pos, 30, text_color,
                                        self.__marqueeText + ' ' + self.__currentSong + ' ')
        marqueetext_pos -= 1
        if marqueetext_pos + text_length < 0:
            marqueetext_pos = self.display.canvas.width

        return marqueetext_pos

    def __render_weather(self, font_small, text_color):
        if self.__weatherTemp is not None:
            weather_string = '%4.1f°C' % self.__weatherTemp
            graphics.DrawText(self.display.canvas, font_small, 34, 20, text_color, weather_string)

    def __render_date_and_time(self, font_big, font_small, text_color):
        time_string = time.strftime('%H:%M:%S')
        graphics.DrawText(self.display.canvas, font_big, 0, 11, text_color, time_string)
        date_string = time.strftime('%d/%m')
        graphics.DrawText(self.display.canvas, font_small, 0, 20, text_color, date_string)

    def set_marquee_text(self, text):
        self.__marqueeText = text
