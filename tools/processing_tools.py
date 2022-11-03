# coding: utf-8

import numpy as np
from PIL import Image
import cv2
from skimage import measure, morphology, util


def _get_base_mask(image: Image) -> np.ndarray:
  """Converts the image to YCbCr, improves the contrast, and selects the pixels
  based on two thresholds on the Cb and Cr channels.

  Args:
    image: The Pillow image to process

  Returns:
    The mask of the selected pixels
  """

  # Switching colorspace and inverting
  image = 255 - np.array(image.convert('YCbCr'))

  # Improving the contrast on the high values of the Cb channel
  blue_diff = image[:, :, 1]
  upper, lower = np.percentile(blue_diff, 99.5), np.percentile(blue_diff, 50)
  blue_diff = np.clip((blue_diff - lower) / (upper - lower) * 255,
                      0, 255).astype('uint8')

  # Improving the contrast on the Cr channel
  red_diff = image[:, :, 2]
  upper, lower = np.percentile(red_diff, 99), np.percentile(red_diff, 1)
  red_diff = np.clip((red_diff - lower) / (upper - lower) * 255,
                     0, 255).astype('uint8')

  del image

  # Returning only the pixels matching the Cb and Cr thresholds
  return (((blue_diff >= 174) & (red_diff <= 130)) * 255).astype('uint8')


def _reindex_labels(base_label: np.ndarray,
                    interest: np.ndarray) -> np.ndarray:
  """Reindex the labels of a labeled image based on a given set of labels to
  keep."""

  # Creating the list of 
  new_index = np.arange(1, base_label.shape[0] + 1)
  to_remap = np.array([index for index in new_index if index not in interest])
  to_leave = np.append(
    np.array([index for index in new_index if index in interest]),
    np.arange(np.max(new_index) + 1, np.max(base_label) + 1))

  base_label = util.map_array(
    base_label, np.append(to_remap, to_leave),
    np.append(np.arange(np.max(base_label) + 1,
                        np.max(base_label) + 1 + len(to_remap)),
              to_leave)).astype('int64')
  return util.map_array(base_label, interest, new_index).astype('int64')


def process_image(img: Image) -> np.ndarray:
  """"""

  # Getting the base mask
  mask = _get_base_mask(img)

  # Removing small holes and small objects in the mask
  mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5)))
  mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5)))

  # Generating the mask for medium objects and detecting all the objects
  mask_medium = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((20, 20)))
  labels_medium = measure.label(mask_medium, background=0, connectivity=2)
  del mask_medium

  # Getting the properties of the detected objects, and selecting the ones
  # that contain at least one hole
  props_medium = measure.regionprops(labels_medium)
  obj_with_hole = np.array([prop.label for prop in props_medium
                            if prop.euler_number < 1])
  try:
    max_size = max((prop.area_filled for prop in props_medium
                    if prop.euler_number < 1))
  except ValueError:
    empty = True
  else:
    empty = False
  del props_medium

  # Processing the medium size objects only if such objects were detected
  if not empty:
    # Reindexing the labels to keep only the ones with a hole
    labels_medium = _reindex_labels(labels_medium, obj_with_hole)
    labels_medium[labels_medium > np.max(obj_with_hole)] = 0
    del obj_with_hole

    # Filling the detected holes and converting to an uint8 image
    labels_medium = morphology.remove_small_holes(labels_medium,
                                                  max_size, connectivity=2)
    mask_medium = ((labels_medium > 0) * 255).astype('uint8')
    del labels_medium

    # Eroding the detected objects back to their original shape
    mask_medium = cv2.morphologyEx(mask_medium, cv2.MORPH_ERODE,
                                   np.ones((20, 20)))

    # Adding the detected big objects to the base mask
    mask = np.maximum(mask, mask_medium)
    del mask_medium
  else:
    del obj_with_hole

  # Detecting all the objects on the new mask
  labels = measure.label(mask, background=0, connectivity=2)
  del mask

  # Getting the properties of the detected objects, and keeping only those with
  # an area bigger than a minimum value
  props = measure.regionprops(labels)
  valid_obj = np.array([prop.label for prop in props
                        if prop.area_filled >= 225])
  del props

  # Testing whether there are valid objects on the image
  try:
    np.max(valid_obj)
  except ValueError:
    empty = True
  else:
    empty = False

  if not empty:
    labels = _reindex_labels(labels, valid_obj)
    labels[labels > np.max(valid_obj)] = 0
  del valid_obj

  # Generating the final uint8 image with all valid objects
  detected = ((labels > 0) * 255).astype('uint8')

  # Detecting each blood vessel
  return measure.label(detected, background=0, connectivity=2)
