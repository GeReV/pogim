import numpy as np
import cv2 as cv
import os

def main():
  filename = '../assets/pogim_2.jpg'

  img = cv.imread(filename, cv.IMREAD_COLOR)

  # img = cv.resize(img, None, fx=0.2, fy=0.2)

  hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

  lower_white = np.array([0,0,215])
  upper_white = np.array([360,15,255])

  # Threshold the HSV image to get only blue colors
  mask = cv.inRange(hsv, lower_white, upper_white)

  inv_mask = cv.bitwise_not(mask)

  image, contours, hierarchy = cv.findContours(inv_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

  contours = filter(lambda cnt: cv.contourArea(cnt) > 500, contours)

  moments = [cv.moments(cnt) for cnt in contours]
  rects = [cv.boundingRect(cnt) for cnt in contours]

  pad = 30

  for index, (x, y, w, h) in enumerate(rects):
    top = y - pad
    bottom = y + h + pad
    left = x - pad
    right = x + w + pad
    section = img[top:bottom, left:right]

    cv.imwrite('{}{:04d}.jpg'.format(os.path.splitext(os.path.basename(filename))[0], index), section)

  for (x, y, w, h) in rects:
    cv.rectangle(img, (x, y), (x+w, y+h), (127, 127, 255))
    cv.rectangle(img, (x - pad, y - pad), (x+w+pad, y+h+pad), (255, 0, 0))

  for moment in moments:
    cx = int(moment['m10']/moment['m00'])
    cy = int(moment['m01']/moment['m00'])
    cv.circle(img, (cx, cy), 2, (0, 0, 255), 2)

  img = cv.drawContours(img, contours, -1, (128, 64, 0), 1)
  
  cv.imshow('image', img)
  cv.waitKey(0)
  cv.destroyAllWindows()

  # max_width = max(rects, key=lambda x:x[2])[2]
  # max_height = max(rects, key=lambda x:x[3])[3]

  


    

if __name__ == '__main__':
  main()
