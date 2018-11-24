import numpy as np
import cv2 as cv
import sys
from os import path


def extract_regions(filename, img, contours, output_size=1200, pad=30):
    for index, cnt in enumerate(contours):
        (x, y, w, h) = cv.boundingRect(cnt)
        top = y - pad
        bottom = y + h + pad
        left = x - pad
        right = x + w + pad

        region = img[top:bottom, left:right]

        (rh, rw, _) = region.shape

        border_bottom = border_top = (output_size - rh) // 2
        border_right = border_left = (output_size - rw) // 2

        border_bottom += output_size - rh - border_bottom - border_top

        border_right += output_size - rw - border_left - border_right

        region = cv.copyMakeBorder(
            region,
            border_top,
            border_bottom,
            border_left,
            border_right,
            cv.BORDER_CONSTANT,
            value=(255, 255, 255)
        )

        out_filename = '{}{:04d}.jpg'.format(
            path.splitext(path.basename(filename))[0], index)

        cv.imwrite(out_filename, region)


def extract_mask(img):
    img = cv.medianBlur(img, 5)
    lab = cv.cvtColor(img, cv.COLOR_BGR2Lab)

    pad = 3

    lower = np.array([128, 128 - pad, 128 - pad])
    upper = np.array([255, 128 + pad, 128 + pad])

    return cv.inRange(lab, lower, upper)


def draw_debug(img, contours, pad=30):
    moments = [cv.moments(cnt) for cnt in contours]
    rects = [cv.boundingRect(cnt) for cnt in contours]

    for (x, y, w, h) in rects:
        cv.rectangle(img, (x, y), (x+w, y+h), (127, 127, 255))
        cv.rectangle(img, (x - pad, y - pad), (x+w+pad, y+h+pad), (255, 0, 0))

    for moment in moments:
        cx = int(moment['m10']/moment['m00'])
        cy = int(moment['m01']/moment['m00'])
        cv.circle(img, (cx, cy), 2, (0, 0, 255), 2)

    img = cv.drawContours(img, contours, -1, (128, 64, 0), 1)

    img = cv.resize(img, None, fx=0.1, fy=0.1)

    cv.imshow('image', img)
    cv.waitKey(0)
    cv.destroyAllWindows()


def extract_pogs(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)

    mask = extract_mask(img)

    inv_mask = cv.bitwise_not(mask)

    image, contours, hierarchy = cv.findContours(
        inv_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = filter(
        lambda cnt: cv.contourArea(cnt) > (img.size // 500),
        contours
    )

    print("Extracting {} Pogs...".format(len(contours)))

    pad = img.shape[0] // 180

    extract_regions(filename, img, contours, pad=pad)

    print("Done.\n")

    # draw_debug(img, contours, pad=pad)


def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE [...FILE]".format(sys.argv[0]))
        exit(1)

    for filename in sys.argv[1:]:
        print("Processing: {}".format(path.abspath(filename)))
        extract_pogs(filename)

    # max_width = max(rects, key=lambda x: x[2])[2] + pad * 2
    # max_height = max(rects, key=lambda x: x[3])[3] + pad * 2

    # print(max_width)
    # print(max_height)


if __name__ == '__main__':
    main()
