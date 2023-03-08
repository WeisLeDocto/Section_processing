# coding: utf-8

# Python >= 3.8 on Windows
import os
from pathlib import Path
if hasattr(os, 'add_dll_directory'):
  with os.add_dll_directory(str(Path(__file__).parent /
                                'openslide-win64' / 'bin')):
    from openslide import OpenSlide
else:
  from openslide import OpenSlide

from pathlib import Path
import numpy as np
import tkinter as tk
from itertools import product
from sys import exit
from gc import collect

from tools import select_folder, get_portion, get_thumbnail, ManualSelection, \
  Progress_window

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

  root.destroy()

  # Getting the paths to the .ndpi images
  images = [file for file in folder.iterdir() if file.suffix == '.ndpi']
  chosen_images = {path: [] for path in images}

  # First, iterating through the images to keep only the valid ones
  for i, img_path in enumerate(images):

    print(f"Now displaying the section : {img_path.stem}")

    slide = OpenSlide(img_path)

    # Getting the thumbnail in a reasonably small size (<4000px)
    thumb_size, factor_thumb = get_thumbnail(slide, 4000)
    img = np.array(slide.get_thumbnail((thumb_size, thumb_size)))

    window = ManualSelection(img, img_path.stem)
    window.mainloop()
    chosen_images[img_path] = window.selection

    collect()

  nb_tile = 4

  root = tk.Tk()
  root.withdraw()

  progress_window = Progress_window('NDPI images :',
                                    'Sections for the current NDPI :')

  nb_sections = sum((len(img_list) for img_list in chosen_images.values()))
  section_count = 0

  # Iterating over all the images
  for img_path in images:

    print(f"Now saving the section : {img_path.stem}")

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
