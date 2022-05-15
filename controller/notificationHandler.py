#!/usr/bin/env python
import urllib.request
import datetime
import json

from rgbmatrix import graphics
from controller.matrix import MatrixController


class NotificationHandler:
    notification = False
    message = ""
    
    __text = "Nachricht"
    __text_pos = 0
    __text_color = graphics.Color(255,255,0) 
    __colorA = graphics.Color(255,0,0) 
    __colorB = graphics.Color(0,255,0) 

    __canvas_width = 64

    def __init__(self, font, canvas: MatrixController.canvas):
        self.font = font
        self.__canvas_width = canvas.width
        pass
    
    def callback_handle_msg(self, msg):
        data = json.loads(msg.decode('UTF-8'))
        #print(data)
        text = data.get("text", None)
        text_color = data.get("color", [255,255,0])
        colorA = data.get("colorA", [255,0,0])
        colorB = data.get("colorB", [255,0,0])
        if(not text or text == ""):
            self.notification = False
        else:
            self.notification = True
            self.__text = data["text"]
            self.__text_color = graphics.Color(text_color[0],text_color[1],text_color[2])
            self.__colorA = graphics.Color(colorA[0],colorA[1],colorA[2])
            self.__colorB = graphics.Color(colorB[0],colorB[1],colorB[2])
                


    def renderNotification(self, canvas: MatrixController.canvas):
        self.__text_pos = self.__render_text(canvas, self.font, self.__text_pos, self.__text_color)
        self.__drawSquare(canvas,[0,19],[63,31],self.__colorA)
        self.__drawSquare(canvas,[1,20],[62,30],self.__colorB)
                        

    def __render_text(self, canvas, font, text_pos, text_color):
        text_length = graphics.DrawText(canvas, font, text_pos, 29, text_color,
                                        self.__text)
        text_pos -= 1
        if text_pos + text_length < 0:
            text_pos = self.__canvas_width

        return text_pos

    def __drawSquare(self, canvas: MatrixController.canvas, c1, c2, color):
        graphics.DrawLine(canvas, c1[0],c1[1],c2[0],c1[1],color)
        graphics.DrawLine(canvas, c2[0],c1[1],c2[0],c2[1],color)
        graphics.DrawLine(canvas, c2[0],c2[1],c1[0],c2[1],color)
        graphics.DrawLine(canvas, c1[0],c2[1],c1[0],c1[1],color)
    
   
