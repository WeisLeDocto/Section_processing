# coding: utf-8

import tkinter as tk
from tkinter import ttk

processing_types = ('Blood vessels', 'Alcian blue', 'Laminin',
                    'MvG', 'MSB', 'S100')


class Processing_choice(tk.Toplevel):
  """This window lets the user choose between a list of available
  post-processing algorithm to apply.

  If no post-processing algorithm is selected, the entire program will
  gracefully stop.
  """

  def __init__(self, choice: tk.StringVar, ok: tk.BooleanVar) -> None:
    """Sets the args and the layout.

    Args:
      choice: A :obj:`tk.StringVar` storing the name of the selected
        post-processing.
      ok: A :obj:`tk.BooleanVar` indicating when the user has made his choice.
    """

    super().__init__()
    self.wm_title('Type of processing')
    self._choice = choice
    self._ok = ok

    tk.Label(self,
             text="Which type of processing to perform ?").pack(side='top',
                                                                padx=5, pady=5)

    # Creating a radio button for each possible post-processing
    for type_ in processing_types:
      ttk.Radiobutton(self, text=type_,
                      variable=choice,
                      value=type_).pack(side='top', padx=5, pady=5)

    # Creating the buttons for validating or cancelling
    ttk.Button(self,
               text='Cancel',
               command=self._cancel).pack(side='right', anchor='e',
                                          padx=5, pady=5)
    ttk.Button(self,
               text='OK',
               command=self._validate).pack(side='left', anchor='e',
                                            padx=5, pady=5)

    self.update()

  def _cancel(self) -> None:
    """Resets the user choice and exits the selection window."""

    self._choice.set('')
    self._ok.set(True)
    self.destroy()

  def _validate(self) -> None:
    """Keeps the user choice and exists the selection window."""

    self._ok.set(True)
    self.destroy()
