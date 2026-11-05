"""Themed widgets shared by the login and sign-up screens.

Both screens are the same design with different copy, so the reusable pieces
live here instead of being copy-pasted into two 150-line Tk constructors.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

from silent_voice import config

PANEL_BG = "#040405"
FIELD_LABEL_FG = "#4f4e4d"
FIELD_TEXT_FG = "#6b6a69"
RULE_COLOUR = "#bdb9b1"
ACCENT = "#3047ff"
FONT = "yu gothic ui"


def load_photo(name: str, size: tuple[int, int] | None = None) -> ImageTk.PhotoImage:
    """Load an asset by filename, independent of the working directory."""
    image = Image.open(config.asset(name))
    if size:
        image = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image)


class AuthScreen:
    """Background image, dark panel, heading and show/hide password field."""

    def __init__(self, window: tk.Tk, title: str, heading: str) -> None:
        self.window = window
        self.window.geometry(config.WINDOW_SIZE)
        self.window.resizable(0, 0)
        self.window.title(title)

        self._images: list[ImageTk.PhotoImage] = []

        background = load_photo("background1.png", (1366, 768))
        self.keep(background)
        panel = tk.Label(window, image=background)
        panel.image = background
        panel.pack(fill="both", expand=True)

        self.frame = tk.Frame(window, bg=PANEL_BG, width=950, height=600)
        self.frame.place(x=200, y=70)

        tk.Label(
            self.frame, text=heading, font=(FONT, 25, "bold"),
            bg=PANEL_BG, fg="white", bd=5, relief="flat",
        ).place(x=80, y=30, width=450, height=30)

        for name, x, y in (("vector.png", 5, 100), ("hyy.png", 620, 130)):
            photo = load_photo(name)
            self.keep(photo)
            label = tk.Label(self.frame, image=photo, bg=PANEL_BG)
            label.image = photo
            label.place(x=x, y=y)

    def keep(self, image: ImageTk.PhotoImage) -> None:
        # Tk does not hold a reference to PhotoImage objects on its own.
        self._images.append(image)

    def add_field(
        self,
        label: str,
        icon: str,
        y_label: int,
        y_entry: int,
        y_rule: int,
        width: int = 270,
        secret: bool = False,
    ) -> tk.Entry:
        tk.Label(
            self.frame, text=label, bg=PANEL_BG, fg=FIELD_LABEL_FG,
            font=(FONT, 13, "bold"),
        ).place(x=550, y=y_label)

        entry = tk.Entry(
            self.frame, highlightthickness=0, relief="flat", bg=PANEL_BG,
            fg=FIELD_TEXT_FG, font=(FONT, 12, "bold"), insertbackground=FIELD_TEXT_FG,
            show="*" if secret else "",
        )
        entry.place(x=580, y=y_entry, width=width)

        tk.Canvas(
            self.frame, width=300, height=2.0, bg=RULE_COLOUR, highlightthickness=0,
        ).place(x=550, y=y_rule)

        photo = load_photo(icon)
        self.keep(photo)
        label_widget = tk.Label(self.frame, image=photo, bg=PANEL_BG)
        label_widget.image = photo
        label_widget.place(x=550, y=y_entry - 2)

        return entry

    def add_submit(self, text: str, command) -> None:
        photo = load_photo("btn1.png")
        self.keep(photo)

        holder = tk.Label(self.frame, image=photo, bg=PANEL_BG)
        holder.image = photo
        holder.place(x=550, y=450)

        button = tk.Button(
            holder, text=text, font=(FONT, 13, "bold"), width=25, bd=0,
            bg=ACCENT, fg="white", cursor="hand2", activebackground=ACCENT,
            command=command,
        )
        button.place(x=20, y=10)

    def attach_password_toggle(self, entry: tk.Entry) -> None:
        """Add the eye button that switches the password field between plain and masked."""
        show_icon = load_photo("show.png")
        hide_icon = load_photo("hide.png")
        self.keep(show_icon)
        self.keep(hide_icon)

        state = {"visible": False}
        button = tk.Button(
            self.frame, image=show_icon, relief="flat", bd=0,
            background="white", activebackground="white", cursor="hand2",
        )

        def toggle() -> None:
            state["visible"] = not state["visible"]
            entry.config(show="" if state["visible"] else "*")
            button.config(image=hide_icon if state["visible"] else show_icon)

        button.config(command=toggle)
        button.place(x=860, y=420)


def show_error(parent: tk.Misc, message: str) -> None:
    messagebox.showerror("Error", message, parent=parent)
