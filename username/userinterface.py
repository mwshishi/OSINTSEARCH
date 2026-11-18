import tkinter as tk
from tkinter import messagebox
import threading
import json, os, webbrowser, time
from username.checkuser import check_username_all_sites
from username.checktwitter import check_twitter_username
from username.checktryhackme import check_tryhackme_username
from database.db_utils import update_username_info


class UsernamePage(tk.Frame):
    def __init__(self, parent, go_back_to):
        super().__init__(parent, bg="#1A2A2A")
        self.parent = parent
        self.go_back_to = go_back_to

        self.status_label = tk.Label(self, text="", font=("Helvetica", 12), fg="yellow", bg="#1A2A2A")
        self.status_label.pack(pady=(10, 0))

        tk.Label(self, text="Username Checker", font=("Helvetica", 16, "bold"), fg="#3CC4BF", bg="#1A2A2A").pack(pady=20)

        tk.Label(self, text="Enter Username:", font=("Helvetica", 12), fg="white", bg="#1A2A2A").pack()
        self.entry = tk.Entry(self, font=("Helvetica", 12), width=30)
        self.entry.pack(pady=5)

        self.check_btn = tk.Button(self, text="Check Username", command=self.check_usernames,
                                   font=("Helvetica", 14), fg="#6DD3CE", bg="#2E4A42",
                                   activeforeground="#1A2A2A", activebackground="#3CC4BF",
                                   relief="ridge", width=20, height=2)
        self.check_btn.pack(pady=10)

        self.result_frame = tk.Frame(self, bg="#1A2A2A")
        self.result_frame.pack(pady=10)

        tk.Button(self, text="Back", command=lambda: parent.show(self.go_back_to),
                  font=("Helvetica", 12), fg="#6DD3CE", bg="#2E4A2A",
                  activeforeground="#1A2A2A", activebackground="#3CC4BF",
                  relief="ridge", width=20, height=2).pack(pady=10)

    def check_usernames(self):
        input_username = self.entry.get().strip()
        if not input_username:
            messagebox.showwarning("Input Error", "Please enter a username.")
            return

        self.status_label.config(text="Checking...", fg="yellow")

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        start_time = time.time()

        def do_check():
            results = check_username_all_sites(input_username)

            def tryhackme_check():
                tryhackme_url, tryhackme_found = check_tryhackme_username(input_username)
                results["TryHackMe"] = (tryhackme_url, tryhackme_found)

                def twitter_check():
                    twitter_url, twitter_found = check_twitter_username(input_username)
                    results["Twitter"] = (twitter_url, twitter_found)

                    elapsed = time.time() - start_time
                    self.parent.after(0, lambda: self.display_results(results, elapsed))

                threading.Thread(target=twitter_check, daemon=True).start()

            threading.Thread(target=tryhackme_check, daemon=True).start()

        threading.Thread(target=do_check, daemon=True).start()

    def display_results(self, results, elapsed):
        self.status_label.config(text=f"Done in {elapsed:.2f} seconds", fg="#3CC4BF")

        # Update DB
        statuses = {site: found for site, (_, found) in results.items()}
        update_username_info(self.entry.get().strip(), statuses)

        for site, (url, found) in results.items():
            color = "green" if found else "red"
            label = tk.Label(self.result_frame, text=f"{site}: {url}",
                            font=("Helvetica", 11), fg=color, bg="#1A2A2A", cursor="hand2")
            label.pack(pady=3)
            label.bind("<Button-1>", lambda e, link=url: webbrowser.open(link))

