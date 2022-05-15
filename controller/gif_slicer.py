#!/usr/bin/env python
import os
from datetime import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import GifImagePlugin

class GifSlicer:
    cacheFolder = "/tmp/"
    imageList = []
    nImages = 0
    __nextImage = 0
    __counter = 0
    __duration = 0

    def loadGif(self, filePath):
        try:
            self.__clearFolder(self.cacheFolder)
            gif = Image.open(filePath)
            #gif.thumbnail((64,32),Image.ANTIALIAS)
            self.nImages = gif.n_frames
            self.__duration = (float(gif.info['duration']) / 1000)
            self.imageList = []
            for frame in range(0,gif.n_frames):
                gif.seek(frame)
                filename = os.path.join(self.cacheFolder, "{:03d}".format(frame) + ".png")
                self.imageList.append(filename)
                gif.save(filename)
            return 1

        except Exception as e:
           print(e)
           self.imageList = []
           self.nImages = 0
           return -1

    def __clearFolder(self, folderPath):
        for f in os.scandir(folderPath):
            if f.name.endswith(".png"):
                os.remove(os.path.join(folderPath, f))

    def getImage(self):
        try:
            image = Image.open(self.imageList[self.__counter])
            image = image.convert('RGB')
            #image.load()
            image.thumbnail((64,32),Image.ANTIALIAS)
            now = datetime.now().timestamp()

            #if __nextImage is older than a full cycle then reset __nextImage
            if(now > (self.__nextImage + (self.__duration * self.nImages))):
                self.__nextImage = now

            if(self.__nextImage < now):
                self.__counter += 1
                self.__nextImage = (self.__nextImage + self.__duration)
                if(self.__counter >= self.nImages):
                    self.__counter = 0

            return image
        except Exception as e:
            print(e)
            return Image.new("RGB",(64,32))
