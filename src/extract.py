import numpy as np
import cv2 as cv
from os import path

def extract_regions(filename, img, contours, output_size=1200, pad=30):
  for index, cnt in enumerate(contours):
    (x, y, w, h) = cv.boundingRect(cnt)
    top = y - pad
    bottom = y + h + pad
    left = x - pad
    right = x + w + pad

    region = img[top:bottom, left:right]

    moment = cv.moments(cnt)
    cx = int(moment['m10']/moment['m00'])
    cy = int(moment['m01']/moment['m00'])

    region_cx = (cx - x + pad)
    region_cy = (cy - y + pad)

    offset_x = (output_size//2) - region_cx
    offset_y = (output_size//2) - region_cy

    (rh, rw, _) = region.shape

    M = np.float32([[1, 0, offset_x],[0, 1, offset_y]])
    region = cv.warpAffine(region, M, (rw,rh), borderMode=cv.BORDER_CONSTANT, borderValue=(255, 255, 255))

    border_top_bottom = (output_size - rh) // 2
    border_left_right = (output_size - rw) // 2

    region = cv.copyMakeBorder(
      region, 
      border_top_bottom, 
      border_top_bottom, 
      border_left_right, 
      border_left_right, 
      cv.BORDER_CONSTANT, 
      value=(255, 255, 255)
    )

    out_filename = '{}{:04d}.jpg'.format(path.splitext(path.basename(filename))[0], index)

    cv.imwrite(out_filename, region)

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

  pad = 60

  extract_regions(filename, img, contours, pad=pad)
  
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
  
  cv.imshow('image', img)
  cv.waitKey(0)
  cv.destroyAllWindows()

  max_width = max(rects, key=lambda x:x[2])[2] + pad * 2
  max_height = max(rects, key=lambda x:x[3])[3] + pad * 2

  print(max_width)
  print(max_height)


    

if __name__ == '__main__':
  main()
