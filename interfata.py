import tkinter as tk
from tkinter import messagebox
import subprocess

# Function to show message on button click
def on_click(option):
    if option == "mail":
        root.destroy()
        subprocess.call(["python", "mail/mailinterface.py"])
    elif option == "admin tools":
        root.destroy()
        subprocess.call(["python", "admintools/admininterface.py"])
    else:
        messagebox.showinfo("Information", f"Wait for the update on {option}")

# Create window
root = tk.Tk()
root.title("OSINT SEARCH")
root.geometry("800x600")
root.configure(bg="#1A2A2A")

# ASCII Title
ascii_title = """
  ___  ____ ___ _   _ _____   ____  _____    _    ____   ____ _   _ 
 / _ \\/ ___|_ _| \\ | |_   _| / ___|| ____|  / \\  |  _ \\ / ___| | | |
| | | \\___ \\| ||  \\| | | |   \\___ \\|  _|   / _ \\ | |_) | |   | |_| |
| |_| |___) | || |\\  | | |    ___) | |___ / ___ \\|  _ <| |___|  _  |
 \\___/|____|___|_| \\_| |_|   |____/|_____/_/   \\_|_| \\_\\\\____|_| |_|
"""

label = tk.Label(root, text=ascii_title, font=("Courier", 10), fg="#3CC4BF", bg="#1A2A2A")
label.pack(pady=20)

# Options List
options = ["mail", "username", "phone number", "instagram","admin tools"]
for option in options:
    button = tk.Button(root, text=option, font=("Helvetica", 14), fg="#6DD3CE", bg="#2E4A42",
                       activeforeground="#1A2A2A", activebackground="#3CC4BF",
                       relief="ridge", width=20, height=2,
                       command=lambda opt=option: on_click(opt))
    button.pack(pady=10)

root.mainloop()