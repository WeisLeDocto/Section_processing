# coding: utf-8

from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional


def select_folder() -> Optional[Path]:
  """Displays a popup window for selecting the working directory.

  Returns:
    The Path object to the selected directory, or None if no directory was
    selected.
  """

  folder = None
  while folder is None:

    # Getting the home folder
    try:
      home_folder = Path.home()
    except RuntimeError:
      home_folder = Path(__file__).parent

    # Asking the user for the directory containing the .ndpi files
    folder = filedialog.askdirectory(initialdir=home_folder,
                                     mustexist=True,
                                     title="Choose the directory containing "
                                           "the .ndpi files")
    # In case the uer clicks Cancel
    if not folder:
      return

    # Making sure the selected folder contains .ndpi files
    folder = Path(folder)
    if not [file for file in folder.iterdir() if file.suffix == '.ndpi']:
      messagebox.showwarning('Hold on !',
                             f'No .ndpi files found in :'
                             f'\n\n{folder}\n\nSelect a correct folder !')
      folder = None

  return folder
