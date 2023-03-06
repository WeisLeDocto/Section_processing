# coding: utf-8

import tkinter as tk
import numpy as np
from matplotlib import pyplot as plt


class Image_choice_window(tk.Toplevel):
  """A window for selecting the image to keep from a given set of sections."""

  def __init__(self,
               *side_images: np.ndarray,
               nr_container: tk.IntVar) -> None:
    """Sets the layout and variables.

    Args:
      side_images: All the images corresponding to one given replica.
      nr_container: An IntVar object storing the number of the chosen image.
    """

    super().__init__()
    self._nr_container = nr_container
    self.attributes('-topmost', True)

    self.wm_title('Image selection window')
    tk.Label(self,
             text='Which image to keep ?').pack(side='top', padx=10,
                                                pady=5, expand=False)

    self._choice = tk.IntVar(value=1)

    # The frame containing the radio buttons
    self._radio_frame = tk.Frame(self)
    self._radio_frame.pack(side='top', expand=True)

    # Creating as many radio buttons as there are images
    for n, _ in enumerate(side_images):
      tk.Radiobutton(self._radio_frame, text=str(n + 1), variable=self._choice,
                     value=n + 1).pack(side='left', padx=5, pady=5,
                                       expand=True)

    # Placing an OK button for validating the choice
    self._ok_button = tk.Button(self, text='OK', command=self._ok_clicked)
    self._ok_button.pack(side='top', pady=5)

    self.resizable = (False, False)

    # Displaying the images to choose from
    fig = plt.figure(1)
    for n, side_img in enumerate(side_images):
      fig.add_subplot(len(side_images), 1, n + 1)
      plt.imshow(side_img)
      plt.ylabel(f'Image {n + 1}')
    plt.show(block=False)

    self.protocol("WM_DELETE_WINDOW", self._ok_clicked)
    self.update()

  def _ok_clicked(self) -> None:
    """Sets the IntVar of the main script, then closes the images and exits."""

    self._nr_container.set(self._choice.get())
    plt.close(1)
    self.destroy()
