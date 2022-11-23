# coding: utf-8

import numpy as np
from PIL import Image
from skimage import measure, segmentation
import tkinter as tk
from pathlib import Path
from xlsxwriter import Workbook
from sys import exit
from gc import collect

from tools import Progress_window, select_folder, detect_section, \
  process_vessels, Processing_choice

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

  # Selecting the type of processing to perform
  choice = tk.StringVar(value='')
  ok = tk.BooleanVar(value=False)
  Processing_choice(choice, ok)
  root.wait_variable(ok)

  # In case the user wants to cancel
  if not choice.get():
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

    print(f"Now processing the section : {fold.stem}")

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

      # Processing for the blood vessel detection
      if choice.get() == 'Blood vessels':

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

            # Counting the overall area
            overall_area += np.count_nonzero(detect_section(img_npy))

            # Detecting the blood vessels
            labels = process_vessels(img)
            del img

            # Saving the outline image
            image_outline = segmentation.mark_boundaries(img_npy[:, :, :3],
                                                         labels,
                                                         color=(0, 1, 0))
            del img_npy
            image_outline = (255 * image_outline).astype('uint8')
            Image.fromarray(image_outline).save(side_fold /
                                                'Processed_images' /
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

      # Any staining that's not the blood vessel detection
      else:

        # Filling the labels in the data sheet
        with Workbook(str(side_fold / 'data.xlsx')) as excel:
          worksheet = excel.add_worksheet()
          bold = excel.add_format({'bold': True, 'align': 'center'})
          worksheet.write(0, 0, "Stained area", bold)
          worksheet.write(1, 0, "Overall area", bold)

          overall_area = 0
          stained_area = 0

          # Iterating over the subsections for processing
          for i, image_path in enumerate((side_fold /
                                          'Raw_images').glob('*.png')):
            # Updating the progress bar
            progress.bottom_progress.set(int(100 * i / nb_img))
            progress.update()

            # Opening the subsection
            img_npy = np.array(Image.open(image_path))

            # Counting the overall area
            overall_area += np.count_nonzero(detect_section(img_npy))

            # Processing for the RGB blue channel
            if choice.get() in ('Alcian blue', 'MSB'):
              # Improving the contrast on the detection of the staining
              blue_chan = img_npy[:, :, 0]
              del img_npy
              if choice.get() == 'MSB':
                upper, lower = 233, 79
              else:
                upper, lower = 221, 92
              blue_chan = ((np.clip(blue_chan, lower, upper) - lower) /
                           (upper - lower) * 255).astype('uint8')

              # Counting the stained area
              stained = ((blue_chan < 160) * 255).astype('uint8')
              del blue_chan

            # Processing on the R, G and B channels
            elif choice.get() == 'MvG':
              stained = (((img_npy[:, :, 0] < 150) &
                          (img_npy[:, :, 1] < 150) &
                          (img_npy[:, :, 2] < 150)) * 255).astype('uint8')

            # Either Laminin or S100, processing the Cr channel
            else:

              # Opening the subsection in YCbCr color space
              img = Image.open(image_path)
              img = img.convert('YCbCr')
              img_npy = np.array(img)
              del img

              # Extracting only the channel of interest
              chan = img_npy[:, :, 2]
              del img_npy

              # Improving the contrast
              upper, lower = 145, 130
              chan = ((np.clip(chan, lower, upper) - lower) /
                      (upper - lower) * 255).astype('uint8')

              # Extracting the stained area
              stained = ((chan > 120) * 255).astype('uint8')
              del chan

            # Counting the stained area
            stained_area += np.count_nonzero(stained)

            # Marking the detected areas as black for MvG
            if choice.get() == 'MvG':
              image_stained = np.stack((255 - stained,
                                        255 - stained,
                                        255 - stained), axis=2)

            # Either Laminin or S100, marking the detected area as red
            elif choice.get() in ('Laminin', 'S100'):
              image_stained = np.stack(
                (np.full(stained.shape, 255).astype('uint8'), 255 - stained,
                 255 - stained), axis=2)

            # Either Alcian blue or MSB, marking the detected area as blue
            else:
              image_stained = np.stack(
                (255 - stained, 255 - stained,
                 np.full(stained.shape, 255).astype('uint8')), axis=2)

            # Saving the stained areas as an image
            del stained
            Image.fromarray(image_stained).save(side_fold /
                                                'Processed_images' /
                                                image_path.name)

            # Ensuring the memory is freed
            collect()

          # Finally, writing the overall and stained areas
          worksheet.write(0, 1, stained_area)
          worksheet.write(1, 1, overall_area)

  progress.destroy()
  root.destroy()
