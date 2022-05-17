#!/usr/bin/python
import socket
import _thread
import time
from PIL import Image
from PIL import ImageDraw

class ArtNet:
    host = ''
    port = 6454
    data = [0]

    __total_w = 64
    __total_h = 32
    __fixture_list = []
    __universe = 0
    image = Image.new("RGB", (32, 32))  # Can be larger than matrix if wanted!!

    def __init__(self, universe = 0, total_w = 64, total_h = 32):
        self.__universe = universe
        self.__total_w = total_w
        self.__total_h = total_h

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.bind((self.host, self.port))

        _thread.start_new_thread(self.parseData, ())

    def addLight(self, addr,x ,y ,w ,h):
        light = {
            "addr" : addr,
            "x": x,
            "y": y,
            "w" : w,
            "h": h
        }
        self.__fixture_list.append(light)

    def parseData(self):
        while 1:
            try:
                message = self.s.recv(8192)
                universe = message[14]
                if (universe == 0):
                    self.data = message[18:]


            except KeyboardInterrupt:
                print("error")
                break

    def printData(self):
            try:
                for light in self.__fixture_list:
                    print("R: " + str(self.data[light["addr"] + -1]))
                    print("G: " + str(self.data[light["addr"] + 0]))
                    print("B: " + str(self.data[light["addr"] + 1]))
                    print("")
            except Exception as e:
                print(e)

            print("----------------------------------")

    def createImage(self):
        self.image = Image.new("RGB",(self.__total_w, self.__total_h))
        try:
            for light in self.__fixture_list:
                x0 = light["x"]
                y0 = light["y"]
                x1 = x0 + light["w"] - 1
                y1 = y0 + light["h"] - 1

                draw = ImageDraw.Draw(self.image)
                draw.rectangle(
                    [(x0, y0), (x1, y1)],
                    fill=(
                        self.data[light["addr"] - 1],
                        self.data[light["addr"]],
                        self.data[light["addr"] + 1],
                    )
                )

#                self.image.paste(
 #                   (
  #                      self.data[light["addr"] - 1],
   #                     self.data[light["addr"]],
    #                    self.data[light["addr"] + 1],
     #                ),
      #          [light["x"], light["y"], light["x"] + light["w"], light["y"] + light["h"]])

        except Exception as e:
            print(e)

if __name__ == "__main__":
    dmx = ArtNet()
    dmx.addLight(1, 0, 0, 0, 0)
    dmx.addLight(4, 0, 0, 0, 0)
    dmx.addLight(7, 0, 0, 0, 0)
    dmx.addLight(10, 0, 0, 0, 0)

    while 1:
        dmx.printData()
        time.sleep(0.5)
