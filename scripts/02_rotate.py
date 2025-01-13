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


def init_renderer(width, height):
    sdl2.ext.init()

    window = sdl2.ext.Window("Rotator", size=(width, height))
    window.show()

    return sdl2.ext.Renderer(window)


def shutdown():
    sdl2.ext.quit()


def rotate_pog(filename, renderer, width, height, rotations_file):

    hw, hh = width // 2, height // 2

    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    sprite = factory.from_image(filename)

    kb_modifiers = sdl2.KMOD_NONE

    angle = 0
    angle_rad = 0

    ruler_y = 0

    running = True

    event = sdl2.SDL_Event()

    while running:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_KEYDOWN or event.type == sdl2.SDL_KEYUP:
                kb_modifiers = event.key.keysym.mod
            if event.type == sdl2.SDL_QUIT:
                running = False
                return False
            if event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym == sdl2.SDLK_RETURN and angle != 0:
                    rotate_image(filename, angle)

                    rotations_file.write(
                        "{}\t{}\n".format(filename, str(angle)))

                    running = False
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
                break

        x, y = ctypes.c_int(0), ctypes.c_int(0)  # Create two ctypes values
        # Pass x and y as references (pointers) to SDL_GetMouseState()
        buttonstate = sdl2.mouse.SDL_GetMouseState(
            ctypes.byref(x),
            ctypes.byref(y)
        )

        if buttonstate & sdl2.SDL_BUTTON(sdl2.SDL_BUTTON_LEFT):
            if kb_modifiers & sdl2.KMOD_CTRL:
                ruler_y = y.value
            else:
                angle_rad = atan2(y.value - height / 2, x.value - width / 2)
                angle = angle_rad * 180 / pi

        renderer.clear(sdl2.ext.Color())
        renderer.copy(sprite, angle=angle)
        renderer.draw_line(
            (
                hw,
                hh,
                hw + int(cos(angle_rad) * hw),
                hh + int(sin(angle_rad) * hh)
            ),
            sdl2.ext.Color(0, 255, 255)
        )

        if ruler_y != 0:
            renderer.draw_line(
                (0, ruler_y, width, ruler_y),
                sdl2.ext.Color(0, 255, 255)
            )

        renderer.present()

    return True


def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE [...FILE]".format(sys.argv[0]))
        exit(1)

    width, height = 1200, 1200

    renderer = init_renderer(width, height)

    rotations_file = open(
        "rotations_{}.txt".format(datetime.now().strftime("%Y%m%d%H%M%S")),
        "w"
    )

    for filename in sys.argv[1:]:
        print("Processing: {}".format(path.abspath(filename)))

        if not rotate_pog(filename, renderer, width, height, rotations_file):
            break

    rotations_file.close()

    shutdown()


if __name__ == "__main__":
    main()
