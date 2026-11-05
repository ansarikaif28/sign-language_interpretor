from tkinter import Tk
from customtkinter import *
from CTkTable import CTkTable
from PIL import Image
import sys
from inference_classifier1 import InferenceClassifier1 as lic




class Application:
    def __init__(self, window):
        self.window = window
        self.window.geometry("856x645")
        self.window.resizable(0, 0)
        self.window.title("Silent Voice")
        
        # Sidebar frame
        self.sidebar_frame = CTkFrame(master=window, fg_color="#000000", width=176, height=650, corner_radius=0)
        self.sidebar_frame.pack_propagate(0)
        self.sidebar_frame.pack(fill="y", side="left")

        self.logo_img_data = Image.open("./images/logo.png")
        self.logo_img = CTkImage(dark_image=self.logo_img_data, light_image=self.logo_img_data, size=(150, 150))  # Increased size
        CTkLabel(master=self.sidebar_frame, text="", image=self.logo_img).pack(pady=(38, 0), anchor="center")

        self.returns_img_data = Image.open("./images/returns_icon.png")
        self.returns_img = CTkImage(dark_image=self.returns_img_data, light_image=self.returns_img_data)
        CTkButton(master=self.sidebar_frame, image=self.returns_img, text="Returns", fg_color="transparent", font=("Arial Bold", 14), hover_color="#333333", anchor="w", text_color="#FFFFFF").pack(anchor="center", ipady=5, pady=(16, 0))

        self.settings_img_data = Image.open("./images/settings_icon.png")
        self.settings_img = CTkImage(dark_image=self.settings_img_data, light_image=self.settings_img_data)
        CTkButton(master=self.sidebar_frame, image=self.settings_img, text="Settings", fg_color="transparent", font=("Arial Bold", 14), hover_color="#333333", anchor="w", text_color="#FFFFFF").pack(anchor="center", ipady=5, pady=(16, 0))

        self.person_img_data = Image.open("./images/person_icon.png")
        self.person_img = CTkImage(dark_image=self.person_img_data, light_image=self.person_img_data)
        CTkButton(master=self.sidebar_frame, image=self.person_img, text="Account", fg_color="transparent", font=("Arial Bold", 14), hover_color="#333333", anchor="w", text_color="#FFFFFF").pack(anchor="center", ipady=5, pady=(160, 0))

        # Main content frame
        self.main_view = CTkFrame(master=self.window, fg_color="#FFFFFF", width=680, height=650, corner_radius=0)
        self.main_view.pack_propagate(0)
        self.main_view.pack(fill="both", expand=True, side="left")

        self.title_frame = CTkFrame(master=self.main_view, fg_color="transparent")
        self.title_frame.pack(anchor="n", fill="x", padx=27, pady=(29, 0))

        CTkLabel(master=self.title_frame, text="Learning From Beginning", font=("Arial Black", 25), text_color="#000000").pack(anchor="nw", side="left")

        self.metrics_frame = CTkFrame(master=self.main_view, fg_color="transparent")
        self.metrics_frame.pack(anchor="n", fill="x", padx=27, pady=(36, 0))

        # Letters Learning Metric
        self.letters_metric = CTkFrame(master=self.metrics_frame, fg_color="#000000", width=400, height=200)
        self.letters_metric.grid_propagate(0)
        self.letters_metric.pack(anchor="center", pady=20, fill="x")

        self.letters_img_data = Image.open("./images/delivered_icon.png")
        self.letters_img = CTkImage(light_image=self.letters_img_data, dark_image=self.letters_img_data, size=(160, 160))

        CTkLabel(master=self.letters_metric, image=self.letters_img, text="").grid(row=0, column=0, rowspan=2, padx=(24, 10), pady=20)
        CTkButton(master=self.letters_metric, text="Interpreting The Letters", text_color="#FFFFFF", font=("Arial Black", 25), fg_color="transparent", hover_color="#333333", command=self.letters_clicked).grid(row=0, column=1, sticky="sw", pady=(0, 20))

        # Numbers Learning Metric
        self.numbers_metric = CTkFrame(master=self.metrics_frame, fg_color="#000000", width=400, height=200)
        self.numbers_metric.grid_propagate(0)
        self.numbers_metric.pack(anchor="center", pady=20, fill="x")

        self.numbers_img_data = Image.open("./images/letter_icon.png")
        self.numbers_img = CTkImage(light_image=self.numbers_img_data, dark_image=self.numbers_img_data, size=(160, 160))

        CTkLabel(master=self.numbers_metric, image=self.numbers_img, text="").grid(row=0, column=0, rowspan=2, padx=(24, 10), pady=20)
        CTkButton(master=self.numbers_metric, text="Interpreting The Numbers", text_color="#FFFFFF", font=("Arial Black", 25), fg_color="transparent", hover_color="#333333", command=self.numbers_clicked).grid(row=0, column=1, sticky="sw", pady=(0, 20))

    def letters_clicked(self):
     
         obj = lic()
         obj.start()
       

    def numbers_clicked(self):
         
         obj = lic()
         obj.start()
      

def page():
    window = Tk()
    Application(window)
    window.mainloop()

if __name__ == '__main__':
    page()