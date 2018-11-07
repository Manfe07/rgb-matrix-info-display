#!/usr/bin/env python
import time

from controller.matrix import MatrixController
from controller.infodisplay import InfoDisplay


def init_matrix():
    matrix_controller = MatrixController()
    InfoDisplay(matrix_controller)


def main():
    init_matrix()
    while True:
        time.sleep(10)


# Main function
if __name__ == '__main__':
    main()
