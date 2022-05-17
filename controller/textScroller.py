#!/usr/bin/env python
import urllib.request
import datetime

from rgbmatrix import graphics
from controller.matrix import MatrixController


class TextScroller:
    text = "Text"
    __text_color = graphics.Color(255,255,255)
    __text_pos = 0
    __canvas_width = 64
    __start = 0
    __end = __canvas_width
    __y = 0


    def __init__(self, font):
        self.__font = font
        pass

    def setFont(self, font):
        self.__font = font

    def setColor(self, color):
        self.__text_color = graphics.Color(color[0],color[1],color[2])

    def setText(self, text,):
        self.text = text


    def renderText(self, canvas: MatrixController.canvas, y, start=0, end=None, font=None, color=None):
        if end:
            self.__end = end
        if font:
            self.__font = font
        if color:
            self.__text_color = graphics.Color(color[0],color[1],color[2])
        self.__y = y
        text_length = graphics.DrawText(canvas, self.__font, self.__text_pos, self.__y, self.__text_color, self.text)
        self.__text_pos -= 1
        if self.__text_pos + text_length < self.__start:
            self.__text_pos = self.__end
