import numpy as np
import cv2 as cv
import sys
from os import path
from math import pi

WINDOW_NAME = "Mask Editor"

SCALE = 0.15

l_value = (0, 255)
a_value = (0, 255)
b_value = (0, 255)
preview_image = None

def clamp(value, a, b):
    return max(a, min(value, b))


def mask(src):
        global l_value
        global a_value
        global b_value

        lower = np.array([l_value[0], a_value[0], b_value[0]])
        upper = np.array([l_value[1], a_value[1], b_value[1]])

        return cv.inRange(src, lower, upper)


def extract_regions(filename, img, circles, pad=30):
    for index, (x, y, r) in enumerate(circles):
        top = max(y - r - pad, 0)
        bottom = y + r + pad
        left = max(x - r - pad, 0)
        right = x + r + pad


        region = img[top:bottom, left:right]

        out_filename = '{}_{:04d}.png'.format(
            path.splitext(path.basename(filename))[0], index)

        cv.imwrite(out_filename, region)


def find_circles(img) -> list[tuple[int, int, int]]:
    min_radius = min(img.shape[0], img.shape[1]) // 20
    max_radius = min(img.shape[0], img.shape[1]) // 2

    circles = cv.HoughCircles(img, cv.HOUGH_GRADIENT, dp=1, minDist=30, param1=100, param2=30, minRadius=min_radius, maxRadius=max_radius)

    if circles is None:
        return []

    return circles[0, :]

def extract_mask(img, pad=3) -> tuple[np.ndarray, list[tuple[int, int, int]]] | None:
    global preview_image
    
    img = cv.medianBlur(img, 5)
    lab = cv.cvtColor(img, cv.COLOR_BGR2Lab)

    preview_image = cv.resize(lab, None, fx=SCALE, fy=SCALE)
    
    update_preview()

    key = cv.waitKey(0)
        
    if key == 13:  # Enter key
        circles = find_circles(mask(preview_image))

        scaled_circles = [(int(x / SCALE), int(y / SCALE), int(r / SCALE)) for (x, y, r) in circles]
        
        return (mask(lab), scaled_circles)
    
    return None


def extract_pogs(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)
    
    if img is None:
        print("Error: Could not read image file: {}".format(filename))
        return
    
    result = extract_mask(img)

    if result is None:
        print("No mask extracted for file: {}".format(filename))
        return
    
    mask, circles = result

    circles = list(filter(
        lambda c: (pi * c[2] ** 2) > (img.shape[0] * img.shape[1] // 500),
        circles
    ))

    print("Extracting {} Pogs...".format(len(circles)))

    pad = img.shape[0] // 180

    extract_regions(filename, img, circles, pad=pad)


def update_preview():
    if preview_image is None:
        return
    
    img = mask(preview_image)

    circles = find_circles(img)

    preview = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles:
            cv.circle(preview, (x, y), r, (0, 0, 255), 2)
    
    cv.imshow(WINDOW_NAME, preview)


def setup_window():
    cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)
    cv.resizeWindow(WINDOW_NAME, 900, 900)

    def on_l_trackbar_min(val):
        global l_value
        l_value = (val, l_value[1])
        update_preview()

    def on_l_trackbar_max(val):
        global l_value
        l_value = (l_value[0], val)
        update_preview()

    def on_a_trackbar_min(val):
        global a_value
        a_value = (val, a_value[1])
        update_preview()

    def on_a_trackbar_max(val):
        global a_value
        a_value = (a_value[0], val)
        update_preview()

    def on_b_trackbar_min(val):
        global b_value
        b_value = (val, b_value[1])
        update_preview()

    def on_b_trackbar_max(val):
        global b_value
        b_value = (b_value[0], val)
        update_preview()

    
    cv.createTrackbar("L Value MIN", WINDOW_NAME, l_value[0],
                      255, on_l_trackbar_min)
    cv.createTrackbar("L Value MAX", WINDOW_NAME, l_value[1],
                      255, on_l_trackbar_max)

    cv.createTrackbar("A Value MIN", WINDOW_NAME, a_value[0],
                      255, on_a_trackbar_min)
    cv.createTrackbar("A Value MAX", WINDOW_NAME, a_value[1],
                      255, on_a_trackbar_max)

    cv.createTrackbar("B Value MIN", WINDOW_NAME, b_value[0],
                      255, on_b_trackbar_min)
    cv.createTrackbar("B Value MAX", WINDOW_NAME, b_value[1],
                      255, on_b_trackbar_max)


def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE [...FILE]".format(sys.argv[0]))
        exit(1)

    setup_window()

    for filename in sys.argv[1:]:
        print("Processing: {}".format(path.abspath(filename)))
        extract_pogs(filename)

    cv.destroyAllWindows()

    print("Done.\n")


if __name__ == '__main__':
    main()
