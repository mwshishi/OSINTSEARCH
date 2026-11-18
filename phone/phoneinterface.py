import customtkinter as ctk
from tkinter import messagebox
import threading, time
from phone.checkphone import check_phone_number
from database.db_utils import update_phone_info, fetch_phone_info  # fetch function added

class PhonePage(ctk.CTkFrame):
    def __init__(self, parent, go_back_to):
        super().__init__(parent, fg_color="#0B0F1A")
        self.parent = parent
        self.go_back_to = go_back_to

        ctk.CTkLabel(self, text="Phone Number Checker", font=("Helvetica", 20, "bold"),
                     text_color="#3CC4BF").pack(pady=20)

        ctk.CTkLabel(self, text="Enter phone number (e.g. +14155552671):",
                     text_color="white", font=("Helvetica", 14)).pack()
        self.phone_entry = ctk.CTkEntry(self, width=300, font=("Helvetica", 14))
        self.phone_entry.pack(pady=10)

        self.check_button = ctk.CTkButton(self, text="Check", command=self.start_check,
                                          fg_color="#2E4A42", hover_color="#3CC4BF",
                                          font=("Helvetica", 14))
        self.check_button.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="yellow", font=("Helvetica", 13))
        self.status_label.pack(pady=5)

        self.result_box = ctk.CTkTextbox(
            self, width=700, height=300, font=("Consolas", 16),
            wrap="word", text_color="white", fg_color="#16202E"
        )
        self.result_box.pack(pady=10)

        ctk.CTkButton(self, text="Back", command=lambda: parent.show(self.go_back_to),
                      fg_color="#2E4A2A", hover_color="#3CC4BF", font=("Helvetica", 13)).pack(pady=10)

    def start_check(self):
        phone = self.phone_entry.get().strip()
        if not phone:
            messagebox.showwarning("Input Error", "Please enter a phone number.")
            return

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.status_label.configure(text="", text_color="yellow")

        def db_check():
            saved_info = fetch_phone_info(phone)
            if saved_info:
                choice = messagebox.askquestion(
                    "Data exists", "This phone number already has saved results.\n\nDo you want to check again?",
                    icon='question'
                )
                if choice == 'no':
                    self.parent.after(0, lambda: self.display_result(saved_info, use_cache=True))
                    return
            self.run_fresh_check(phone)

        threading.Thread(target=db_check, daemon=True).start()

    def run_fresh_check(self, phone):
        self.check_button.configure(state="disabled")
        self.status_label.configure(text="Checking...", text_color="yellow")
        start_time = time.time()

        def check_thread():
            try:
                info = check_phone_number(phone)

                if "error" in info:
                    # Show error in result box
                    self.parent.after(0, lambda: self.display_result({"Error": info["error"]}))
                else:
                    update_phone_info(phone, info)
                    elapsed = time.time() - start_time
                    self.parent.after(0, lambda: self.display_result(info, elapsed))
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.parent.after(0, lambda: self.check_button.configure(state="normal"))


        threading.Thread(target=check_thread, daemon=True).start()

    def display_result(self, info, elapsed=None, use_cache=False):
        if use_cache:
            self.status_label.configure(text="Loaded from database", text_color="orange")
        elif elapsed is not None:
            self.status_label.configure(text=f"Check complete in {elapsed:.2f} seconds", text_color="#3CC4BF")

        result_lines = [f"{k}: {v}" for k, v in info.items()]
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", "\n".join(result_lines))
        self.result_box.configure(state="disabled")
