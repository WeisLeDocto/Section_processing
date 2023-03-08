# coding: utf-8

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np
from PIL import Image, ImageTk
from typing import Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class Box:
  """"""

  bbox: Tuple[int, int, int, int]


class ManualSelection(tk.Tk):
  """"""

  def __init__(self, thumbnail: np.ndarray, name: str) -> None:
    """"""

    super().__init__()

    self.title(f"Selection on the scan: {name}")
    self._img = thumbnail
    self._image_tk = None
    self._img_width = 1000
    self.selection = list()

    self._rectangles: List[Optional[int]] = [None, None, None]
    self._current = 0
    self._start = (0., 0.)

    self._left_label_var = tk.StringVar(value="Left section : X")
    self._center_label_var = tk.StringVar(value="Center section : X")
    self._right_label_var = tk.StringVar(value="Right section : X")
    self._label_vars = [self._left_label_var, self._center_label_var,
                        self._right_label_var]

    self._set_layout()
    self._set_bindings()

    self.update()
    self.protocol("WM_DELETE_WINDOW", self._save_and_exit)

  def _set_layout(self) -> None:
    """"""

    # The main frame of the window
    self._frm = ttk.Frame()
    self._frm.pack(fill='both', expand=True)

    self._img_frame = ttk.Frame(self._frm)
    self._img_frame.pack(expand=True, fill="both", anchor="w", side="left",
                         padx=5, pady=5)

    pil_img = Image.fromarray(self._img)
    img_ratio = pil_img.height / pil_img.width
    height = int(self._img_width * img_ratio)
    pil_img = pil_img.resize((self._img_width, height))
    self._image_tk = ImageTk.PhotoImage(pil_img)
    self._img_canvas = tk.Canvas(self._img_frame, width=self._img_width,
                                 height=height)
    self._img_canvas.pack(fill='both', expand=True)
    self._img_canvas.create_image(int(self._img_width / 2), int(height / 2),
                                  anchor='center', image=self._image_tk)

    # The frame containing the buttons
    self._aux_frame = ttk.Frame(self._frm)
    self._aux_frame.pack(expand=False, fill="both", anchor="e", side='right')

    self._left_label = ttk.Label(self._aux_frame,
                                 textvariable=self._left_label_var)
    self._left_label.pack(fill="x", anchor="n", side='top', padx=10,
                          pady=5, expand=False)

    self._center_label = ttk.Label(self._aux_frame,
                                   textvariable=self._center_label_var)
    self._center_label.pack(fill="x", anchor="n", side='top', padx=10,
                            pady=5, expand=False)

    self._right_label = ttk.Label(self._aux_frame,
                                  textvariable=self._right_label_var)
    self._right_label.pack(fill="x", anchor="n", side='top', padx=10,
                           pady=5, expand=False)

    self._next_button = ttk.Button(self._aux_frame, text="Next",
                                   command=self._next_clicked)
    self._next_button.pack(fill="x", anchor="n", side='top', padx=10,
                           pady=5, expand=False)

  def _set_bindings(self) -> None:
    """"""

    self._img_canvas.bind('<ButtonPress-1>', self._start_box)
    self._img_canvas.bind('<B1-Motion>', self._extend_box)
    self._img_canvas.bind('<ButtonRelease-1>', self._stop_box)

  def _start_box(self, event: tk.Event) -> None:
    """"""

    if self._current > 2:
      return

    if self._rectangles[self._current] is not None:
      self._img_canvas.delete(self._rectangles[self._current])
      self._rectangles[self._current] = None

    self._start = (event.x, event.y)

  def _extend_box(self, event: tk.Event) -> None:
    """"""

    if self._current > 2:
      return

    if self._rectangles[self._current] is None:
     self._rectangles[self._current] = self._img_canvas.create_rectangle(
       (self._start[0], self._start[1], event.x, event.y))

    else:
      self._img_canvas.coords(self._rectangles[self._current],
                              self._start[0], self._start[1], event.x, event.y)

  def _stop_box(self, event: tk.Event) -> None:
    """"""

    if self._current > 2:
      return

    self._img_canvas.coords(self._rectangles[self._current],
                            self._start[0], self._start[1], event.x, event.y)

  def _next_clicked(self) -> None:
    """"""

    if self._rectangles[self._current] is None:
      messagebox.showerror("Error !", "Please select a section before "
                                      "switching to the next column.")

    self._label_vars[self._current].set(
      self._label_vars[self._current].get().replace('X', 'OK'))
    self._current += 1

    if self._current > 2:
      self._save_and_exit()

  def _save_and_exit(self) -> None:
    """"""

    if self._current < 3:
      messagebox.showerror("Error !", "Please select all the sections before "
                                      "exiting.")
      return

    pil_width, pil_height = self._image_tk.width(), self._image_tk.height()
    img_height, img_width, *_ = self._img.shape

    for i in range(3):
      x0, y0, x1, y1 = self._img_canvas.coords(self._rectangles[i])

      x0 = int(x0 / pil_width * img_width)
      x1 = int(x1 / pil_width * img_width)
      y0 = int(y0 / pil_height * img_height)
      y1 = int(y1 / pil_height * img_height)

      self.selection.append(Box((y0, x0, y1, x1)))

    self.destroy()
