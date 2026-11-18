import customtkinter as ctk
from pagemanager import PageManager
from tkinter import messagebox
from mail.mailinterface import MailPage
from admintools.admininterface import AdminPage
from username.userinterface import UsernamePage
from phone.phoneinterface import PhonePage
from admintools.reportinterface import ReportPage

from photo.photointerface import PhotoPage
from PIL import Image, ImageTk
from tkinter import Canvas
import pywinstyles
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# === Page: Main Menu ===
class MainMenuPage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.configure(fg_color="transparent")

        # === Stretchable background ===
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.original_bg = None
        if os.path.exists("assets/backround2.jpg"):
            self.original_bg = Image.open("assets/backround2.jpg")
            self.update_background()

        self.bind("<Configure>", self.on_resize)

        # === Banner image ===
        if os.path.exists("assets/osint.png"):
            banner_img = Image.open("assets/osint.png").resize((533, 260))
            banner_img_tk = ctk.CTkImage(light_image=banner_img, size=(513, 240))
            banner_label = ctk.CTkLabel(self, image=banner_img_tk, text="", bg_color="#000001")
            banner_label.image = banner_img_tk
            banner_label.pack(pady=(10, 0))
            pywinstyles.set_opacity(banner_label, color="#000001")

        # === Button data ===
        self.buttons = []
        button_data = [
            ("Mail", "assets/email.png", lambda: self.parent.show(lambda p: MailPage(p, go_back_to=MainMenuPage))),
            ("Username", "assets/user.png", lambda: self.parent.show(lambda p: UsernamePage(p, go_back_to=MainMenuPage))),
            ("Phone Number", "assets/phone.png", lambda: self.parent.show(lambda p: PhonePage(p, go_back_to=MainMenuPage))),
            ("Photo Upload", "assets/instagram.png", lambda: self.parent.show(lambda p: PhotoPage(p, go_back_to=MainMenuPage))),
            ("OSINT report", "assets/research.png", lambda: self.parent.show(lambda p: ReportPage(p, go_back_to=MainMenuPage))),
            ("Admin Tools", "assets/admintools.png", lambda: self.parent.show(lambda p: AdminPage(p, go_back_to=MainMenuPage)))
        ]

        for i, (label_text, icon_path, action) in enumerate(button_data):
            if action is None:
                action = lambda opt=label_text: messagebox.showinfo("Info", f"Wait for the update on {opt}")

            image = None
            if icon_path and os.path.exists(icon_path):
                img = Image.open(icon_path).resize((40, 40))
                image = ImageTk.PhotoImage(img)

            button = ctk.CTkButton(
                master=self,
                text=label_text,
                image=image,
                compound="left",
                corner_radius=20,
                width=500,
                height=70,
                fg_color="#0B0F1A",
                hover_color="#16202e",
                text_color="white",
                border_color="#00BFFF",
                border_width=1,
                font=("Helvetica", 19, "bold"),
                anchor="w",
                bg_color="#101624",
                command=action
            )
            button.image = image
            button.place(relx=0.5, y=230 + i * 85, anchor="center")
            pywinstyles.set_opacity(button, color="#101624")
            self.buttons.append(button)

    def on_resize(self, event):
        self.update_background()
        self.center_buttons()

    def update_background(self):
        if self.original_bg:
            width = self.winfo_width()
            height = self.winfo_height()
            if width > 0 and height > 0:
                resized = self.original_bg.resize((width, height), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(resized)
                self.bg_label.configure(image=self.bg_image)

    def center_buttons(self):
        for i, button in enumerate(self.buttons):
            button.place_configure(relx=0.5, anchor="center", y=270 + i * 85)


# === Main App Runner ===
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("OSINT SEARCH")
    app.geometry("1200x700")
    app.configure(fg_color="#101624")

    manager = PageManager(app)
    manager.show(MainMenuPage)


    # === Safe close handler ===
    def on_closing():
        current = manager.current_page
        if isinstance(current, ReportPage) and current.has_unsaved_bubbles():
            result = messagebox.askyesno(
                "Unsaved Report",
                "You have an unsaved report in progress. If you close this window, the report will be invalidated. Continue?"
            )
            if not result:
                return
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)

    app.mainloop()

