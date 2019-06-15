import numpy as np
import cv2 as cv
import sys
from os import path

WINDOW_NAME = "Mask Editor"


def clamp(value, a, b):
    return max(a, min(value, b))


def extract_regions(filename, img, contours, pad=30):
    for index, cnt in enumerate(contours):
        (x, y, w, h) = cv.boundingRect(cnt)
        top = y - pad
        bottom = y + h + pad
        left = x - pad
        right = x + w + pad

        region = img[top:bottom, left:right]

        out_filename = '{}_{:04d}.png'.format(
            path.splitext(path.basename(filename))[0], index)

        cv.imwrite(out_filename, region)


l_value = (0, 255)
a_value = (0, 255)
b_value = (0, 255)


def extract_mask(img, pad=3):
    img = cv.medianBlur(img, 5)
    lab = cv.cvtColor(img, cv.COLOR_BGR2Lab)

    lab_resize = cv.resize(lab, None, fx=0.15, fy=0.15)

    cv.namedWindow(WINDOW_NAME)

    def mask(src):
        global l_value

        lower = np.array([l_value[0], a_value[0], b_value[0]])
        upper = np.array([l_value[1], a_value[1], b_value[1]])

        return cv.inRange(src, lower, upper)

    def on_l_trackbar_min(val):
        global l_value
        l_value = (val, l_value[1])
        cv.imshow(WINDOW_NAME, mask(lab_resize))

    def on_l_trackbar_max(val):
        global l_value
        l_value = (l_value[0], val)
        cv.imshow(WINDOW_NAME, mask(lab_resize))

    def on_a_trackbar_min(val):
        global a_value
        a_value = (val, a_value[1])
        cv.imshow(WINDOW_NAME, mask(lab_resize))

    def on_a_trackbar_max(val):
        global a_value
        a_value = (a_value[0], val)
        cv.imshow(WINDOW_NAME, mask(lab_resize))

    def on_b_trackbar_min(val):
        global b_value
        b_value = (val, b_value[1])
        cv.imshow(WINDOW_NAME, mask(lab_resize))

    def on_b_trackbar_max(val):
        global b_value
        b_value = (b_value[0], val)
        cv.imshow(WINDOW_NAME, mask(lab_resize))

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

    cv.imshow(WINDOW_NAME, mask(lab_resize))

    cv.waitKey(0)
    cv.destroyAllWindows()

    return mask(lab)


def draw_debug(img, contours, pad=30):
    rects = [cv.boundingRect(cnt) for cnt in contours]

    for (x, y, w, h) in rects:
        cv.rectangle(img, (x, y), (x+w, y+h), (127, 127, 255))
        cv.rectangle(img, (x - pad, y - pad), (x+w+pad, y+h+pad), (255, 0, 0))

    img = cv.drawContours(img, contours, -1, (128, 64, 0), 1)

    img = cv.resize(img, None, fx=0.15, fy=0.15)

    cv.imshow('image', img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def extract_pogs(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)

    mask = extract_mask(img)

    inv_mask = cv.bitwise_not(mask)

    contours, hierarchy = cv.findContours(
        inv_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = list(filter(
        lambda cnt: cv.contourArea(cnt) > (img.size // 500),
        contours
    ))

    print("Extracting {} Pogs...".format(len(contours)))

    pad = img.shape[0] // 180

    extract_regions(filename, img, contours, pad=pad)
    # draw_debug(img, contours, pad=pad)

    print("Done.\n")


def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE [...FILE]".format(sys.argv[0]))
        exit(1)

    for filename in sys.argv[1:]:
        print("Processing: {}".format(path.abspath(filename)))
        extract_pogs(filename)


if __name__ == '__main__':
    main()
