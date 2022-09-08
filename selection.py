# coding: utf-8

from openslide import OpenSlide
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from skimage import measure, morphology
import tkinter as tk
from tkinter import messagebox
from itertools import product
from sys import exit
from gc import collect

from tools import Progress_window, detect_section, select_folder, \
  Image_choice_window, get_image, get_portion, get_thumbnail


if __name__ == '__main__':

  # Base hidden window, necessary for using the TopLevel
  root = tk.Tk()
  root.withdraw()

  # Getting the path to working directory
  folder = select_folder()

  # In case the user wants to cancel
  if folder is None:
    root.destroy()
    exit()

  # Getting the paths to the .ndpi images
  images = [file for file in folder.iterdir() if file.suffix == '.ndpi']

  # Displaying the progress bar
  progress_window = Progress_window('NDPI images :',
                                    'Sections for the current NDPI :')

  valid_images = {path: [] for path in images}

  # First, iterating through the images to keep only the valid ones
  for i, img_path in enumerate(images):

    # Updating the progress bar
    progress_window.top_progress.set(int(100 * i / len(images)))
    progress_window.update()

    slide = OpenSlide(img_path)

    # Getting the thumbnail in a reasonably small size (<4000px)
    thumb_size, factor_thumb = get_thumbnail(slide, 4000)
    img = np.array(slide.get_thumbnail((thumb_size, thumb_size)))

    # Converting to gray, thresholding, blurring, smoothening and inverting
    img = detect_section(img)

    # Detecting the continuous areas and removing the smaller ones
    labels = measure.label(img, background=0, connectivity=2)

    labels = morphology.remove_small_objects(labels, min_size=20000,
                                             connectivity=2)
    label_props = measure.regionprops(labels)

    # Workaround to get the number of labels
    k = 0
    while True:
      try:
        _ = label_props[k]
        k += 1
      except IndexError:
        label_len = k
        break

    # Iterating over the detected areas and asking the user if they're valid
    for j, label in enumerate(label_props):

      # Updating the progress bar
      progress_window.bottom_progress.set(int(100 * j / label_len))
      progress_window.update()

      # Displaying the detected area
      plt.imshow(get_image(slide, label, factor_thumb, 10000))
      plt.show(block=False)

      # Asking the user
      ret = messagebox.askyesno('Image validity',
                                'Is the displayed image valid ?')
      plt.close('all')

      # If the user's ok, adding the image to the list of valid ones
      if ret:
        valid_images[img_path].append(label)

  img_nr = tk.IntVar(value=1)
  chosen_images = {path: [] for path in images}

  # Iterating over the replicates of a same section to pick only one
  for i, img_path in enumerate(images):

    # Updating the progress bar
    progress_window.top_progress.set(int(100 * i / len(images)))
    progress_window.update()

    # Opening the image
    slide = OpenSlide(img_path)
    labels = valid_images[img_path]

    # Getting the thumbnail in a reasonably small size (<4000px)
    _, factor_thumb = get_thumbnail(slide, 4000)

    # Sorting the labels according to their x position
    left, center, right = [], [], []
    for label in labels:
      _, x = label.centroid
      if x < 1000:
        left.append(label)
      elif x > 2300:
        right.append(label)
      else:
        center.append(label)

    # For each side, asking the user which section to keep
    count = 0
    for side in (left, center, right):

      # Updating the progress bar
      progress_window.bottom_progress.set(int(100 * count / len(labels)))
      progress_window.update()

      count += len(side)

      # If there are images on the given side, displaying the choice window
      if side:
        images_side = [get_image(slide, label, factor_thumb, 4000)
                       for label in side]
        Image_choice_window(*images_side, nr_container=img_nr)
        root.wait_variable(img_nr)

        # Storing the paths to the chosen images
        chosen_images[img_path].append(side[img_nr.get() - 1])

  # Updating the progress bar
  nb_tile = 4
  progress_window.top_progress.set(0)
  progress_window.bottom_progress.set(0)
  progress_window.update()

  nb_sections = sum((len(img_list) for img_list in chosen_images.values()))
  section_count = 0

  # Iterating over all the images
  for img_path in images:

    # Opening the image
    slide = OpenSlide(img_path)

    # Getting the thumbnail in a reasonably small size (<4000px)
    _, factor_thumb = get_thumbnail(slide, 4000)

    # Iterating over the selected sections to divide them and save them
    for j, label in enumerate(chosen_images[img_path]):

      # Updating the progress bar
      progress_window.top_progress.set(int(100 * section_count / nb_sections))
      progress_window.update()
      section_count += 1

      nr_to_dir = {0: 'Left', 1: 'Center', 2: 'Right'}

      # Creating the folder for storing the subsections
      Path.mkdir(img_path.parent / f'{img_path.stem}' / f'{nr_to_dir[j]}' /
                 'Raw_images', exist_ok=True, parents=True)

      # Iterating over each subsection
      for k, (x, y) in enumerate(product(range(nb_tile), range(nb_tile))):

        # Updating the progress bar
        progress_window.bottom_progress.set(int(100 * k / (nb_tile * nb_tile)))
        progress_window.update()

        # Saving the subsection
        get_portion(slide, label, factor_thumb, 4, x, y).save(
          img_path.parent / f'{img_path.stem}' / f'{nr_to_dir[j]}' /
          'Raw_images' / f'Section_{x + 1}_{y + 1}.png')

        # Ensuring the memory is freed
        collect()

  progress_window.destroy()
  root.destroy()
