#!/usr/bin/env python
import time
import configparser

from controller.matrix import MatrixController
from controller.infodisplay import InfoDisplay

config = configparser.ConfigParser()
config.read('config.yaml')


def init_matrix():
    matrix_controller = MatrixController()
    InfoDisplay(config, matrix_controller)


def main():
    init_matrix()
    while True:
        time.sleep(10)


# Main function
if __name__ == '__main__':
    main()
