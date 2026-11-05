"""Login screen."""

from __future__ import annotations

import tkinter as tk

from silent_voice import auth, config
from silent_voice.ui.auth_screen import AuthScreen, load_photo, show_error

HEADING = "WELCOME To Silent Voice"


class LoginPage:
    def __init__(self, window: tk.Tk) -> None:
        self.window = window
        self.screen = AuthScreen(window, "Silent Voice - Login", HEADING)
        frame = self.screen.frame

        tk.Label(
            frame, text="Sign In", bg="#040405", fg="white",
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
        self.screen.add_submit("LOGIN", self.authenticate)

        tk.Label(
            frame, text="No account yet?", font=("yu gothic ui", 11, "bold"),
            relief="flat", borderwidth=0, background="#040405", fg="white",
        ).place(x=550, y=560)

        register = load_photo("register.png")
        self.screen.keep(register)
        tk.Button(
            frame, image=register, bg="#040405", cursor="hand2", borderwidth=0,
            background="#040405", activebackground="#040405",
            command=self.open_signup,
        ).place(x=670, y=555, width=111, height=35)

        self.window.bind("<Return>", lambda _event: self.authenticate())

        if not auth.is_configured():
            show_error(
                self.window,
                "Firebase is not configured, so sign-in will fail.\n\n"
                "Copy .env.example to .env and set FIREBASE_API_KEY.",
            )

    def authenticate(self) -> None:
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            session = auth.sign_in(email, password)
        except auth.AuthError as exc:
            show_error(self.window, exc.message)
            return

        self.window.destroy()
        from silent_voice.ui.home import Application

        root = tk.Tk()
        Application(root, session=session)
        root.mainloop()

    def open_signup(self) -> None:
        self.window.destroy()

        from silent_voice.ui.signup import SignUp

        root = tk.Tk()
        SignUp(root)
        root.mainloop()


def page() -> None:
    window = tk.Tk()
    LoginPage(window)
    window.mainloop()


if __name__ == "__main__":
    page()
