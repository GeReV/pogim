import numpy as np
import cv2 as cv
import sys
from os import path

WINDOW_NAME = "Mask Editor"
PREVIEW_WINDOW_NAME = "Preview"

blur_value = 5
l_value = (0, 255)
a_value = (0, 255)
b_value = (0, 255)


def mask(src):
    global l_value

    lower = np.array([l_value[0], a_value[0], b_value[0]])
    upper = np.array([l_value[1], a_value[1], b_value[1]])

    return cv.inRange(src, lower, upper)


def extract_mask(img):
    global blur_value

    img = cv.medianBlur(img, blur_value * 2 + 1)
    lab = cv.cvtColor(img, cv.COLOR_BGR2Lab)

    return mask(lab)


def blend(a, b, alpha):
    a = a.astype(float) / 255
    b = b.astype(float) / 255

    alpha = alpha.astype(float) / 255

    a = cv.multiply(alpha, a)

    b = cv.multiply(1.0 - alpha, b)

    return np.uint8(cv.add(a, b) * 255)


def clean_pog(img):
    mask = extract_mask(img)

    inv_mask = cv.bitwise_not(mask)

    contours, hierarchy = cv.findContours(
        inv_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    contours = list(filter(
        lambda cnt: cv.contourArea(cnt) > (img.size // 500),
        contours
    ))

    alpha = np.zeros(img.shape)

    for cnt in contours:
        (x, y), radius = cv.minEnclosingCircle(cnt)

        alpha = cv.circle(
            alpha,
            (int(x), int(y)),
            int(radius),
            (1, 1, 1),
            -1
        )

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

    return blend(white, img, alpha)


def show_preview(img):
    cv.namedWindow(WINDOW_NAME)
    cv.namedWindow(PREVIEW_WINDOW_NAME)

    resize = cv.resize(img, None, fx=0.5, fy=0.5)

    def update_preview():
        cv.imshow(WINDOW_NAME, extract_mask(resize))
        cv.imshow(PREVIEW_WINDOW_NAME, clean_pog(resize))

    def on_blur_trackbar(val):
        global blur_value
        blur_value = val
        update_preview()

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

    cv.createTrackbar("Blur Value", WINDOW_NAME, blur_value,
                      50, on_blur_trackbar)

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

    update_preview()

    cv.waitKey(0)
    cv.destroyAllWindows()


def main():
    if len(sys.argv) == 1:
        print("Usage: {} FILE [...FILE]".format(sys.argv[0]))
        exit(1)

    for filename in sys.argv[1:]:
        print("Cleaning: {}".format(path.abspath(filename)))

        img = cv.imread(filename, cv.IMREAD_COLOR)

        show_preview(img)

        result = clean_pog(img)

        cv.imwrite(filename, result)


if __name__ == '__main__':
    main()
