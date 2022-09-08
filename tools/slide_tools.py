# coding: utf-8

from openslide import OpenSlide
import numpy as np


def get_image(ndpi_slide: OpenSlide,
              img_label,
              thumb_factor: int,
              max_pix: int) -> np.ndarray:
  """Function that takes a zone of the slide as an input, and returns the same
  zone in a different zoom factor.

  Args:
    ndpi_slide: The OpenSlide object containing the image.
    img_label: The scikit-image label containing the target area of the slide.
    thumb_factor: The zoom factor used for obtaining the first image.
    max_pix: The maximum dimension of the returned image in pixels.

  Returns:
    The same image as the input thumbnail but with a different zoom factor.
  """

  # Getting the bbox of the label
  min_y, min_x, max_y, max_x = img_label.bbox
  size_max = max(max_x - min_x, max_y - min_y)

  # Calculating the minimum zoom factor so that the area represented by the
  # bbox with the thumb_factor zoom level fits in the given max dimension
  ratio = min((m for m in range(10)
               if size_max * 2 ** thumb_factor / 2 ** m < max_pix))

  # Calculating the new dimensions of the images
  x_size = int((max_x - min_x) * (2 ** (thumb_factor - ratio)))
  y_size = int((max_y - min_y) * (2 ** (thumb_factor - ratio)))

  # Calculating the new origin coordinates of the image
  min_x = min_x * 2 ** thumb_factor
  min_y = min_y * 2 ** thumb_factor

  # Returning the wanted image
  return ndpi_slide.read_region((min_x, min_y), ratio, (x_size, y_size))


def get_portion(ndpi_slide: OpenSlide,
                img_label,
                thumb_factor: int,
                n_slices: int,
                x_id: int,
                y_id: int) -> np.ndarray:
  """Function that takes a zone of a slide as an input, and returns a
  subsection of this zone in the 0 zoom level.

  Args:
    ndpi_slide: The OpenSlide object containing the image.
    img_label: The scikit-image label containing the target area of the slide.
    thumb_factor: The zoom factor used for obtaining the first image.
    n_slices: The number of subsections the entire image will be cut to in each
      direction.
    x_id: The index of the subsection along the x-axis.
    y_id: The index of the subsection along the y-axis.

  Returns:
    A subsection of the input image in the 0 zoom level.
  """

  min_y, min_x, max_y, max_x = img_label.bbox

  # Calculating the dimension of the subsection
  x_size = int((max_x - min_x) * (2 ** thumb_factor) / n_slices)
  y_size = int((max_y - min_y) * (2 ** thumb_factor) / n_slices)

  # Calculating the origin of the subsection
  min_x = min_x * 2 ** thumb_factor + x_id * x_size
  min_y = min_y * 2 ** thumb_factor + y_id * y_size

  # Returning the actual subsection
  return ndpi_slide.read_region((min_x, min_y), 0, (x_size, y_size))


def get_thumbnail(open_slide, max_size):
  """Function that takes an OpenSlide object and returns a thumbnail
  representing it entirely.

  Args:
    open_slide: The OpenSlide object to draw.
    max_size: The maximum size in pixels of the thumbnail.

  Returns:
    A thumbnail of the slide.
  """

  max_ = max(open_slide.dimensions)
  size, factor = max(((max_ / 2 ** i_, i_) for i_ in range(10)
                      if max_ / 2 ** i_ < max_size))
  return size, factor
