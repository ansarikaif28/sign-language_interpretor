"""Dashboard shown after a successful sign-in."""

from __future__ import annotations

import threading
import tkinter as tk

from customtkinter import CTkButton, CTkFrame, CTkImage, CTkLabel
from PIL import Image

from silent_voice import config
from silent_voice.auth import Session
from silent_voice.ui.auth_screen import load_photo, show_error
from silent_voice.vision.predict import run_webcam

SIDEBAR_WIDTH = 176
DARK = "#000000"


def _ctk_image(name: str, size: tuple[int, int] | None = None) -> CTkImage:
    image = Image.open(config.asset(name))
    return CTkImage(dark_image=image, light_image=image, size=size)


class Application:
    def __init__(self, window: tk.Tk, session: Session | None = None) -> None:
        self.window = window
        self.session = session
        self.window.geometry(config.DASHBOARD_SIZE)
        self.window.resizable(0, 0)
        self.window.title("Silent Voice")

        self._build_sidebar()
        self._build_main_view()

    def _build_sidebar(self) -> None:
        sidebar = CTkFrame(master=self.window, fg_color=DARK, width=SIDEBAR_WIDTH,
                           height=650, corner_radius=0)
        sidebar.pack_propagate(0)
        sidebar.pack(fill="y", side="left")

        CTkLabel(master=sidebar, text="", image=_ctk_image("logo.png", (150, 150))) \
            .pack(pady=(38, 0), anchor="center")

        for label, icon in (
            ("Returns", "returns_icon.png"),
            ("Settings", "settings_icon.png"),
        ):
            CTkButton(master=sidebar, image=_ctk_image(icon), text=label,
                      fg_color="transparent", font=("Arial Bold", 14),
                      hover_color="#333333", anchor="w", text_color="#FFFFFF") \
                .pack(anchor="center", ipady=5, pady=(16, 0))

        account_text = "Account"
        if self.session and self.session.email:
            account_text = self.session.email.split("@")[0]

        CTkButton(master=sidebar, image=_ctk_image("person_icon.png"), text=account_text,
                  fg_color="transparent", font=("Arial Bold", 14),
                  hover_color="#333333", anchor="w", text_color="#FFFFFF") \
            .pack(anchor="center", ipady=5, pady=(160, 0))

    def _build_main_view(self) -> None:
        main = CTkFrame(master=self.window, fg_color="#FFFFFF", width=680,
                        height=650, corner_radius=0)
        main.pack_propagate(0)
        main.pack(fill="both", expand=True, side="left")

        title = CTkFrame(master=main, fg_color="transparent")
        title.pack(anchor="n", fill="x", padx=27, pady=(29, 0))
        CTkLabel(master=title, text="Learning From Beginning",
                 font=("Arial Black", 25), text_color="#000000") \
            .pack(anchor="nw", side="left")

        cards = CTkFrame(master=main, fg_color="transparent")
        cards.pack(anchor="n", fill="x", padx=27, pady=(36, 0))

        self._build_card(cards, "delivered_icon.png", "Interpreting The Letters")
        self._build_card(cards, "letter_icon.png", "Interpreting The Numbers")

    def _build_card(self, parent, icon: str, title: str) -> None:
        card = CTkFrame(master=parent, fg_color=DARK, width=400, height=200)
        card.grid_propagate(0)
        card.pack(anchor="center", pady=20, fill="x")

        CTkLabel(master=card, image=_ctk_image(icon, (160, 160)), text="") \
            .grid(row=0, column=0, rowspan=2, padx=(24, 10), pady=20)

        CTkButton(master=card, text=title, text_color="#FFFFFF",
                  font=("Arial Black", 25), fg_color="transparent",
                  hover_color="#333333", command=self.open_interpreter) \
            .grid(row=0, column=1, sticky="sw", pady=(0, 20))

    def open_interpreter(self) -> None:
        """Start the webcam loop on a worker thread so Tk does not freeze."""
        self.window.withdraw()

        def work() -> None:
            try:
                run_webcam()
            except Exception as error:  # bind the message now: `error` is cleared on exit
                message = str(error)
                self.window.after(0, lambda: show_error(self.window, message))
            finally:
                self.window.after(0, self.window.deiconify)

        threading.Thread(target=work, daemon=True).start()


def page() -> None:
    window = tk.Tk()
    Application(window)
    window.mainloop()


if __name__ == "__main__":
    page()
