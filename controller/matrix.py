#!/usr/bin/env python
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class MatrixController:
    matrix = None
    canvas = None
    options = None

    def __init__(self):
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        #self.options.gpio_slowdown = 4
        # self.options.pwm_bits = 8
        self.options.pwm_lsb_nanoseconds = 310
        #self.options.disable_hardware_pulsing = 1
        #self.options.chain_length = 2
        #self.options.parallel = 1
        self.options.hardware_mapping = 'adafruit-hat'

        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()

        print('Instance of MatrixController created!')
