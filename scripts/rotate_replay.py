# -*- coding: utf-8 -*-
import sdl2
import sdl2.ext
import sdl2.mouse
import ctypes
import sys
from subprocess import call
from os import path
from math import atan2, pi, sin, cos
from datetime import datetime


def rotate_image(filename, angle):
    fullpath = path.abspath(filename)

    return call(["convert", fullpath, "-distort", "SRT", "1 %f" % angle, fullpath])

def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE".format(sys.argv[0]))
        exit(1)

    rotations_file = open(sys.argv[1], "r")

    for line in rotations_file:
        filename, angle = line.split()

        print(angle)
        print("Processing: {}".format(path.abspath(filename)))

        rotate_image(filename, float(angle))

    rotations_file.close()


if __name__ == "__main__":
    main()
