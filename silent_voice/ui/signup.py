"""Sign-up screen."""

from __future__ import annotations

import tkinter as tk

from silent_voice import auth
from silent_voice.ui.auth_screen import AuthScreen, load_photo, show_error

HEADING = "WELCOME TO THE TEAM !!!"


class SignUp:
    def __init__(self, window: tk.Tk) -> None:
        self.window = window
        self.screen = AuthScreen(window, "Silent Voice - Sign Up", HEADING)
        frame = self.screen.frame

        tk.Label(
            frame, text="Sign Up", bg="#040405", fg="white",
            font=("yu gothic ui", 17, "bold"),
        ).place(x=650, y=240)

        self.email_entry = self.screen.add_field(
            "Email", "username_icon.png", y_label=300, y_entry=335, y_rule=359,
        )
        self.password_entry = self.screen.add_field(
            "Password", "password_icon.png", y_label=380, y_entry=416,
            y_rule=440, width=244, secret=True,
        )
        self.screen.attach_password_toggle(self.password_entry)
        self.screen.add_submit("SIGN UP", self.create_account)

        tk.Label(
            frame, text="Already registered?", font=("yu gothic ui", 11, "bold"),
            relief="flat", borderwidth=0, background="#040405", fg="white",
        ).place(x=550, y=560)

        login_icon = load_photo("register.png")
        self.screen.keep(login_icon)
        tk.Button(
            frame, image=login_icon, bg="#040405", cursor="hand2", borderwidth=0,
            background="#040405", activebackground="#040405",
            command=self.open_login,
        ).place(x=670, y=555, width=111, height=35)

        self.window.bind("<Return>", lambda _event: self.create_account())

    def create_account(self) -> None:
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            session = auth.sign_up(email, password)
        except auth.AuthError as exc:
            show_error(self.window, exc.message)
            return

        self.window.destroy()
        from silent_voice.ui.home import Application

        root = tk.Tk()
        Application(root, session=session)
        root.mainloop()

    def open_login(self) -> None:
        self.window.destroy()

        from silent_voice.ui.login import LoginPage

        root = tk.Tk()
        LoginPage(root)
        root.mainloop()


def page() -> None:
    window = tk.Tk()
    SignUp(window)
    window.mainloop()


if __name__ == "__main__":
    page()
