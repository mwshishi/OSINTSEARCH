import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import re

PHOTO_DIR = "photo"

class PhotoPage(ctk.CTkFrame):
    def __init__(self, parent, go_back_to):
        super().__init__(parent, fg_color="#0B0F1A")
        self.parent = parent
        self.go_back_to = go_back_to
        self.current_folder = None
        self.photo_widgets = []

        ctk.CTkLabel(self, text="Photo Manager", font=("Helvetica", 20, "bold"), text_color="#3CC4BF").pack(pady=20)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Create Folder", command=self.show_create_popup,
                      fg_color="#2E4A42", hover_color="#3CC4BF").grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Load Folder", command=self.load_folder_dialog,
                      fg_color="#2E4A42", hover_color="#3CC4BF").grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Back", command=lambda: parent.show(self.go_back_to),
                      fg_color="#2E4A2A", hover_color="#3CC4BF").grid(row=0, column=2, padx=10)

        self.upload_button = ctk.CTkButton(self, text="Upload Photo", command=self.upload_photo,
                                           fg_color="#3C4F2F", hover_color="#3CC4BF")
        self.upload_button.pack(pady=5)
        self.upload_button.pack_forget()

        self.scrollable = ctk.CTkScrollableFrame(self, width=700, height=400, fg_color="#16202E")
        self.scrollable.pack(pady=20)

    def show_create_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Create Folder")
        popup.geometry("350x150")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Enter folder name:", font=("Helvetica", 13)).pack(pady=10)
        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)

        def create():
            name = entry.get().strip()
            if not name or not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
                messagebox.showerror("Error", "Invalid folder name.")
                return
            path = os.path.join(PHOTO_DIR, name)
            if os.path.exists(path):
                if messagebox.askyesno("Exists", "Folder already exists. Open it?"):
                    self.switch_to_folder(name)
                popup.destroy()
            else:
                os.makedirs(path)
                self.switch_to_folder(name)
                popup.destroy()

        ctk.CTkButton(popup, text="Create", command=create).pack(pady=10)

    def load_folder_dialog(self):
        folders = [f for f in os.listdir(PHOTO_DIR) if os.path.isdir(os.path.join(PHOTO_DIR, f))]
        if not folders:
            messagebox.showinfo("No Folders", "No folders found in 'photo/'.")
            return
        popup = ctk.CTkToplevel(self)
        popup.title("Select Folder")
        popup.geometry("350x200")
        popup.grab_set()

        var = ctk.StringVar(value=folders[0])
        menu = ctk.CTkOptionMenu(popup, values=folders, variable=var)
        menu.pack(pady=20)

        def load():
            self.switch_to_folder(var.get())
            popup.destroy()

        ctk.CTkButton(popup, text="Load", command=load).pack(pady=10)

    def switch_to_folder(self, folder_name):
        self.current_folder = folder_name
        self.upload_button.pack(pady=5)
        self.display_photos()

    def upload_photo(self):
        if not self.current_folder:
            return

        filepath = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if not filepath:
            return

        filename_base = os.path.splitext(os.path.basename(filepath))[0]
        popup = ctk.CTkToplevel(self)
        popup.title("Add Photo Metadata")
        popup.geometry("400x300")
        popup.grab_set()

        name_entry = ctk.CTkEntry(popup)
        name_entry.insert(0, filename_base)
        name_entry.pack(pady=10)

        desc_entry = ctk.CTkEntry(popup, placeholder_text="Description (optional)")
        desc_entry.pack(pady=10)

        source_entry = ctk.CTkEntry(popup, placeholder_text="Source (optional)")
        source_entry.pack(pady=10)

        def save_photo():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Name cannot be empty.")
                return

            dest_img = os.path.join(PHOTO_DIR, self.current_folder, new_name + os.path.splitext(filepath)[1])
            if os.path.exists(dest_img):
                messagebox.showerror("Error", "A photo with this name already exists.")
                return

            shutil.copy(filepath, dest_img)
            meta_path = os.path.splitext(dest_img)[0] + ".txt"
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(f"Description: {desc_entry.get().strip() or 'N/A'}\n")
                f.write(f"Source: {source_entry.get().strip() or 'N/A'}\n")

            self.display_photos()
            popup.destroy()

        ctk.CTkButton(popup, text="Add Photo to Folder", command=save_photo).pack(pady=20)

    def display_photos(self):
        for widget in self.photo_widgets:
            widget.destroy()
        self.photo_widgets.clear()

        folder_path = os.path.join(PHOTO_DIR, self.current_folder)
        files = sorted(os.listdir(folder_path))

        for file in files:
            if not file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                continue

            image_path = os.path.join(folder_path, file)
            text_path = os.path.splitext(image_path)[0] + ".txt"

            try:
                image = Image.open(image_path)
                image.thumbnail((300, 300))
                tk_img = ImageTk.PhotoImage(image)
            except:
                continue

            frame = ctk.CTkFrame(self.scrollable, fg_color="#1C2A3A")
            frame.pack(pady=10, fill="x")

            img_label = ctk.CTkLabel(frame, image=tk_img, text="")
            img_label.image = tk_img
            img_label.pack()

            if os.path.exists(text_path):
                with open(text_path, "r", encoding="utf-8") as f:
                    meta = f.read()
            else:
                meta = "Description: N/A\nSource: N/A"

            meta_label = ctk.CTkLabel(frame, text=meta, text_color="white", font=("Consolas", 13), justify="left")
            meta_label.pack(pady=5)

            self.photo_widgets.append(frame)
