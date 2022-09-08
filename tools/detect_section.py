# coding: utf-8

import cv2
import numpy as np


def detect_section(img: np.ndarray) -> np.ndarray:
  """Image processing function for detecting the section areas over the
  background.

  Args:
    img: The base color image to process.

  Returns:
    A grey level image, with 255 being the section areas and 0 the background.
  """

  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  _, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY)
  img = cv2.GaussianBlur(img, (21, 21), 0)
  img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((10, 10)))
  _, img = cv2.threshold(img, 210, 255, cv2.THRESH_BINARY)
  img = 255 - img

  return img
