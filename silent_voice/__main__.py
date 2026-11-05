"""Entry point: ``python -m silent_voice`` launches the login screen."""

from __future__ import annotations

import tkinter as tk

from silent_voice import config
from silent_voice.ui.login import LoginPage


def main() -> None:
    config.ensure_dirs()
    window = tk.Tk()
    LoginPage(window)
    window.mainloop()


if __name__ == "__main__":
    main()
