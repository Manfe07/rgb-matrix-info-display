#!/usr/bin/env python

import os
from PIL import Image, ImageSequence, GifImagePlugin


class GifParser:
    def __init__(self, filename):
        self.im = Image.open(filename)
        index = 0
        size = 12, 12

        self.data = list()
        for frame in ImageSequence.Iterator(self.im):
            index += 1
            im = frame.copy()
            im = im.resize(size)
            rgb_im = im.convert('RGB')
            self.data.append(rgb_im)
        self.numFrames = index
        # frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
        # self.frames = [frame.thumbnail(size) for frame in ImageSequence.Iterator(frames)]

        # Display individual frames from the loaded animated GIF file

    def get_frame(self, i):
        im = self.data[i-1]
        
        return im

    @staticmethod
    def get_pixel(x, y, rgb_im):
        r, g, b = rgb_im.getpixel((x, y))
        return r, g, b
