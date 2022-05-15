#!/usr/bin/env python
import datetime
import json

from PIL import Image
from PIL import ImageDraw


class Weather:
    temp = 12.3
    icon = Image.new("RGB", (12,12))
    image_path = "weather/"
    __icon_id = None


    def parseData(self, msg):
        data = json.loads(msg.decode('UTF-8'))
        self.temp = float(data["tempc"])
        id = data["icon"]

        if(id != self.__icon_id):
            image = Image.new("RGB", (12,12))
            if((id == "01d") or (id == "01n")):
                image = Image.open(self.image_path + "sun.png")
            elif((id == "02d") or (id == "02n")):
                image = Image.open(self.image_path + "cloud_sun.png")
            elif((id == "03d") or (id == "03n")):
                image = Image.open(self.image_path + "cloud.png")
            elif((id == "04d") or (id == "04n")):
                image = Image.open(self.image_path + "cloud.png")
            elif((id == "09d") or (id == "09n")):
                image = Image.open(self.image_path + "cloud_rain.png")
            elif((id == "10d") or (id == "10n")):
                image = Image.open(self.image_path + "cloud_sun_rain.png")
            image = image.convert('RGB')
            image.load()
            image.thumbnail((12,12),Image.ANTIALIAS)
            self.icon = image
            self.__icon_id = id
