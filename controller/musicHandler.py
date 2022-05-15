#!/usr/bin/env python
import urllib.request
import datetime
import json

from PIL import Image
from PIL import ImageDraw

class MusicHandler:
    state = "paused"
    title = "title"
    artist = "artist"
    album = "album"
    image_path = "/cover.jpg"
    cover = Image.new("RGB", (32, 32))  # Can be larger than matrix if wanted!!
    percentFinished = 0.0
    start = datetime.datetime.now().timestamp()
    duration = 100
    __oldImageURL = ""

    def downloadImage(self, url):
        try:
            urllib.request.urlretrieve(url, self.image_path)

            image = Image.open(self.image_path)
            image = image.convert('RGB')
            image.load()
            image.thumbnail((20,20),Image.ANTIALIAS)
            self.cover = image
            self.__oldImageURL = url

        except Exception as e:
            print("music")
            print(e)

    def parseMsg(self, msg):
        data = json.loads(msg.decode('UTF-8'))
        track = data["track"]
        #print(data)
        self.state = data["state"]
        if(self.state == "playing"):
            self.title = track.get("title", "")
            self.artist = track.get("artist", "")
            self.album = track.get("album", "")
            self.duration = float(track.get("duration", "100"))
            position = float(track.get("position", "001"))
            self.start = datetime.datetime.now().timestamp() - position
            try:
                self.percentFinished = float(position / self.duration)
            except:
                self.percentFinished = 0
            url = track.get("albumArtURI","https://www.iconsdb.com/icons/preview/white/musical-note-xxl.png")

            if(url != self.__oldImageURL):
                self.downloadImage(track.get("albumArtURI","https://www.iconsdb.com/icons/preview/white/musical-note-xxl.png"))

