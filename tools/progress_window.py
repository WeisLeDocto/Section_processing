# coding: utf-8

import tkinter as tk
from tkinter import ttk


class Progress_window(tk.Toplevel):
  """Displays a popup window allowing to follow the progress of the image
  processing."""

  def __init__(self, top_title, bottom_title) -> None:
    """Sets the layout and the variables.

    Args:
      top_title: The title of the top progress bar.
      bottom_title: The title of the bottom progress bar.
    """

    super().__init__()
    self.wm_title('Progress bar')
    self.attributes('-topmost', True)

    # Variables storing the progress of both bars
    self.top_progress = tk.IntVar(value=0)
    self.bottom_progress = tk.IntVar(value=0)

    # Creating the top bar and its label
    tk.Label(self, text=top_title).pack(side='top', padx=5, pady=5)
    self._top_bar = ttk.Progressbar(self, orient='horizontal',
                                    mode='determinate', length=280,
                                    variable=self.top_progress)
    self._top_bar.pack(side='top', pady=5, padx=5)

    # Creating the bottom bar and its label
    tk.Label(self, text=bottom_title).pack(side='top', padx=5, pady=5)
    self._bottom_bar = ttk.Progressbar(self, orient='horizontal',
                                       mode='determinate', length=280,
                                       variable=self.bottom_progress)
    self._bottom_bar.pack(side='top', pady=5, padx=5)
