#!/usr/bin/env python
import datetime
import re


class Playlist:
    screens = []
    duration = 120
    __currentPos = 0
    __nextScreen = 0

    def __init__(self, duration : int, screens: list = None):
        if screens:
            self.screens = screens
        self.duration = duration
        pass

    def set(self, duration : int = None, screens: list = None):
        if screens:
            self.screens = screens

        if duration:
            self.duration = duration


    def getScreen(self):
        try:
            now = datetime.datetime.now().timestamp()

            if(now > self.__nextScreen):
                self.__currentPos += 1
                self.__nextScreen = now + self.duration

            if(self.__currentPos >= self.screens.__len__()):
                self.__currentPos = 0

            return self.screens[self.__currentPos]

        except Exception as e:
            print(e)
            return 0   # Return default Screen
