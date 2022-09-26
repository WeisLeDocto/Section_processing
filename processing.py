# coding: utf-8

import numpy as np
from PIL import Image
from skimage import measure, segmentation
import tkinter as tk
from pathlib import Path
from xlsxwriter import Workbook
from sys import exit
from gc import collect

from tools import Progress_window, select_folder, detect_section, process_image

if __name__ == '__main__':

  # Base hidden window, necessary for using the TopLevel
  root = tk.Tk()
  root.withdraw()

  # Selecting the working folder
  folder = select_folder()

  # In case the user wants to cancel
  if folder is None:
    root.destroy()
    exit()

  # Getting all the sub-folders containing the .png images
  folders = [fold for fold in folder.iterdir() if fold.is_dir()
             and list(fold.rglob('*.png'))]
  nb_fold = sum((len([dir_ for dir_ in fold.iterdir() if dir_.is_dir()
                      and list(dir_.rglob('*.png'))]) for fold in folders))
  fold_count = 0

  # Creating the progress bar window
  progress = Progress_window('Processed sections :',
                             'Processed subsections :')

  # Iterating over all the folders
  for fold in folders:
    # iterating over all the sub-folders containing .png images
    for side_fold in [dir_ for dir_ in fold.iterdir() if dir_.is_dir()
                      and list(dir_.rglob('*.png'))]:

      # Updating the progress bar
      progress.top_progress.set(int(100 * fold_count / nb_fold))
      progress.update()
      fold_count += 1
      nb_img = len(list((side_fold / 'Raw_images').glob('*.png')))

      # Creating the Excel data sheet
      Path.mkdir(side_fold / 'Processed_images', exist_ok=True, parents=True)

      # Filling the labels in the data sheet
      with Workbook(str(side_fold / 'data.xlsx')) as excel:
        worksheet = excel.add_worksheet()
        bold = excel.add_format({'bold': True, 'align': 'center'})
        worksheet.write(0, 0, "Vessel index", bold)
        worksheet.write(0, 1, "Vessel smaller diameter", bold)
        worksheet.write(0, 2, "Vessel area", bold)
        worksheet.write(0, 3, "Vessel perimeter", bold)
        worksheet.write(0, 4, "", bold)
        worksheet.write(0, 5, "Overall area", bold)
        index = 1

        overall_area = 0

        # Iterating over the subsections for processing
        for i, image_path in enumerate((side_fold /
                                        'Raw_images').glob('*.png')):

          # Updating the progress bar
          progress.bottom_progress.set(int(100 * i / nb_img))
          progress.update()

          # Opening the subsection
          img = Image.open(image_path)
          img_npy = np.array(img)

          # Detecting the blood vessels
          detected = process_image(img)
          del img

          # Detecting each blood vessel and saving the outlined image
          labels = measure.label(detected, background=0, connectivity=2)
          del detected
          image_outline = segmentation.mark_boundaries(img_npy[:, :, :3],
                                                       labels, color=(0, 1, 0))

          # Counting the overall area
          overall_area += np.count_nonzero(detect_section(img_npy))
          del img_npy

          image_outline = (255 * image_outline).astype('uint8')
          Image.fromarray(image_outline).save(side_fold / 'Processed_images' /
                                              image_path.name)
          del image_outline

          # Calculating the vessels properties and storing them in the Excel
          label_props = measure.regionprops(labels)
          del labels
          for prop in label_props:
            worksheet.write(index, 0, index)
            worksheet.write(index, 1, prop.axis_minor_length)
            worksheet.write(index, 2, prop.area_filled)
            worksheet.write(index, 3, prop.perimeter)
            index += 1

          # Ensuring the memory is freed
          collect()

        # Finally, writing the overall section area
        worksheet.write(1, 5, overall_area)

  progress.destroy()
  root.destroy()
