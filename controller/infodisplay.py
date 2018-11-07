#!/usr/bin/env python
import os
import time
import _thread
import requests

from rgbmatrix import graphics
from controller.matrix import MatrixController
from controller.gifparser import GifParser


class InfoDisplay:
    __marqueeText = ''
    __currentSong = 'Hier könnte Ihre Werbung stehen.   '
    __weatherTemp = None

    def __init__(self, matrix_controller: MatrixController):
        self.display = matrix_controller
        _thread.start_new_thread(self.__render_loop, ())
        _thread.start_new_thread(self.__external_data_fetcher, ())
        print('Render thread is running.')

    @staticmethod
    def __load_font(filename):
        font = graphics.Font()
        font.LoadFont(os.path.dirname(os.path.realpath(__file__)) + 'fonts/' + filename)
        return font

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
        text_color = graphics.Color(10, 5, 5)
        # text_color = graphics.Color(80, 80, 100)

        marqueetext_pos = self.display.canvas.width

        gif = GifParser('assets/eq.gif')
        gif_counter = 0
        gif_delay = 0

        while True:
            self.display.canvas.Clear()

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
                self.display.canvas.SetPixel(x - 1, y + 20, r / 10, g / 10, b / 10)

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
