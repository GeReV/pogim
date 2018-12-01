import numpy as np
import cv2 as cv
import sys
from os import path


def extract_mask(img):
    img = cv.medianBlur(img, 5)
    lab = cv.cvtColor(img, cv.COLOR_BGR2Lab)

    pad = 5

    lower = np.array([128, 128 - pad, 128 - pad])
    upper = np.array([255, 128 + pad, 128 + pad])

    return cv.inRange(lab, lower, upper)


def blend(a, b, alpha):
    a = a.astype(float) / 255
    b = b.astype(float) / 255

    alpha = alpha.astype(float) / 255

    a = cv.multiply(alpha, a)

    b = cv.multiply(1.0 - alpha, b)

    return np.uint8(cv.add(a, b) * 255)


def clean_pog(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)
    mask = extract_mask(img)

    inv_mask = cv.bitwise_not(mask)

    image, contours, hierarchy = cv.findContours(
        inv_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = filter(
        lambda cnt: cv.contourArea(cnt) > (img.size // 500),
        contours
    )

    alpha = np.zeros(img.shape)

    for cnt in contours:
        (x, y), radius = cv.minEnclosingCircle(cnt)

        alpha = cv.circle(alpha, (int(x), int(y)), int(
            radius), (1, 1, 1), -1)

    alpha = 1 - alpha

    alpha = cv.GaussianBlur(alpha, (51, 51), 0, 0)
    alpha = cv.circle(
        alpha,
        (int(x), int(y)),
        int(radius),
        (0, 0, 0),
        -1
    )

    alpha = np.clip((alpha - 0.5) * 2, 0.0, 1.0)
    alpha = np.uint8(alpha * 255)

    white = np.ones(img.shape, np.uint8) * 255

    img = blend(white, img, alpha)

    cv.imwrite(filename, img)


def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE [...FILE]".format(sys.argv[0]))
        exit(1)

    for filename in sys.argv[1:]:
        print("Cleaning: {}".format(path.abspath(filename)))
        clean_pog(filename)


if __name__ == '__main__':
    main()
