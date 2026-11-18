import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
import sys, os
import psycopg2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mail.checkemail import check_email
from database.db_utils import update_email_info

class MailPage(tk.Frame):
    def __init__(self, parent, go_back_to):
        super().__init__(parent, bg="#1A2A2A")

        self.go_back_to = go_back_to
        self.parent = parent

        tk.Label(self, text="Email Checker", font=("Helvetica", 16, "bold"), fg="#3CC4BF", bg="#1A2A2A").pack(pady=20)

        tk.Label(self, text="Enter Email:", font=("Helvetica", 12), fg="white", bg="#1A2A2A").pack()
        self.email_entry = tk.Entry(self, font=("Helvetica", 12), width=30)
        self.email_entry.pack(pady=5)

        self.check_button = tk.Button(self, text="Check Email", font=("Helvetica", 14), fg="#6DD3CE", bg="#2E4A42",
                                      activeforeground="#1A2A2A", activebackground="#3CC4BF",
                                      relief="ridge", width=20, height=2, command=self.check_existing)
        self.check_button.pack(pady=20)

        self.status_label = tk.Label(self, text="", font=("Helvetica", 12), fg="white", bg="#1A2A2A")
        self.status_label.pack(pady=5)

        self.result_frame = tk.Frame(self, bg="#1A2A2A")
        self.result_frame.pack(pady=10)

        tk.Button(self, text="Back", command=lambda: parent.show(self.go_back_to),
                  font=("Helvetica", 12), fg="#6DD3CE", bg="#2E4A2A",
                  activeforeground="#1A2A2A", activebackground="#3CC4BF",
                  relief="ridge", width=20, height=2).pack(pady=10)

    def check_existing(self):
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Input Error", "Please enter an email address.")
            return

        try:
            conn = psycopg2.connect(host="localhost", database="osintSearchDB", user="postgres", password="admin", port="5432")
            cur = conn.cursor()
            cur.execute("SELECT * FROM email_info WHERE email = %s", (email,))
            exists = cur.fetchone()
            cur.close()
            conn.close()

            if exists:
                self.show_existing_popup(email)
                return
        except Exception as e:
            print("[DB CHECK ERROR]", e)

        self.update_results(email, force_all=True)

    def show_existing_popup(self, email):
        popup = tk.Toplevel(self)
        popup.title("Email Exists")
        popup.configure(bg="#1A2A2A")
        popup.geometry("400x250")

        tk.Label(popup, text="Email already exists in the database.\nWhat would you like to do?",
                 font=("Helvetica", 12), fg="white", bg="#1A2A2A").pack(pady=20)

        tk.Button(popup, text="1) No, just give me the available information.",
                  command=lambda: [popup.destroy(), self.load_existing_results(email)],
                  font=("Helvetica", 11), bg="#2E4A42", fg="#6DD3CE").pack(pady=5)

        tk.Button(popup, text="2) Yes, check everything again.",
                  command=lambda: [popup.destroy(), self.update_results(email, force_all=True)],
                  font=("Helvetica", 11), bg="#2E4A42", fg="#6DD3CE").pack(pady=5)

        tk.Button(popup, text="3) Yes, but only check 'Not Found'",
                  command=lambda: [popup.destroy(), self.check_if_not_found_exists_then_update(email)],
                  font=("Helvetica", 11), bg="#2E4A42", fg="#6DD3CE").pack(pady=5)

        tk.Button(popup, text="4) No, go back.", command=popup.destroy,
                  font=("Helvetica", 11), bg="#2E4A42", fg="#6DD3CE").pack(pady=5)

    def load_existing_results(self, email):
        try:
            conn = psycopg2.connect(host="localhost", database="osintSearchDB", user="postgres", password="admin", port="5432")
            cur = conn.cursor()
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'email_info' AND column_name LIKE '%_status';")
            columns = [row[0] for row in cur.fetchall()]

            if not columns:
                self.parent.after(0, lambda: messagebox.showinfo("Info", "No status columns found."))
                return

            status_query = ", ".join(f'"{col}"' for col in columns)
            cur.execute(f"SELECT {status_query} FROM email_info WHERE email = %s", (email,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            for widget in self.result_frame.winfo_children():
                widget.destroy()

            if not row:
                self.status_label.config(text="No info found.", fg="red")
                return

            self.status_label.config(text="Existing info:", fg="#3CC4BF")

            for i, col in enumerate(columns):
                site = col.replace("_status", "").capitalize()
                found = row[i]
                color = "green" if found == "Found" else "red"
                text = f"{site}: {found}"
                label = tk.Label(self.result_frame, text=text, font=("Helvetica", 12), fg=color, bg="#1A2A2A")
                label.pack(pady=5)

        except Exception as e:
            print("[DB FETCH ERROR]", e)

    def check_if_not_found_exists_then_update(self, email):
        try:
            conn = psycopg2.connect(host="localhost", database="osintSearchDB", user="postgres", password="admin", port="5432")
            cur = conn.cursor()
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'email_info' AND column_name LIKE '%_status';")
            columns = [f'"{row[0]}"' for row in cur.fetchall()]

            if not columns:
                self.parent.after(0, lambda: messagebox.showinfo("Info", "No status columns found."))
                return

            status_query = ", ".join(columns)
            cur.execute(f"SELECT {status_query} FROM email_info WHERE email = %s", (email,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row or all(value == "Found" for value in row if value != "N/A"):
                self.parent.after(0, lambda: messagebox.showinfo("Info", "No 'Not Found' entries to check."))
                return

            if any(value == "Not Found" for value in row if value != "N/A"):
                self.update_results(email, force_all=False)

        except Exception as e:
            print("[DB FETCH ERROR]", e)

    def run_async_check(self, email, callback, check_only_not_found):
        def thread_func():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(check_email(email))
                loop.close()
                callback(result, check_only_not_found)
            except Exception as e:
                print("[ERROR]", e)
                callback(None, check_only_not_found)

        threading.Thread(target=thread_func).start()

    def update_results(self, email, force_all):
        self.check_button.config(state="disabled")
        self.status_label.config(text="Checking...", fg="yellow")

        def show_results(results, check_only_not_found):
            self.check_button.config(state="normal")
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            if not results:
                self.status_label.config(text="Error during check.", fg="red")
                return

            self.status_label.config(text="Check complete!", fg="#3CC4BF")

            final_results = {}
            if check_only_not_found:
                existing = {}
                try:
                    conn = psycopg2.connect(host="localhost", database="osintSearchDB", user="postgres", password="admin", port="5432")
                    cur = conn.cursor()
                    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'email_info' AND column_name LIKE '%_status';")
                    columns = [f'"{row[0]}"' for row in cur.fetchall()]

                    status_query = ", ".join(columns)
                    cur.execute(f"SELECT {status_query} FROM email_info WHERE email = %s", (email,))
                    row = cur.fetchone()
                    cur.close()
                    conn.close()

                    if row:
                        for i, col in enumerate(columns):
                            site = col.replace('"', '').replace("_status", "").capitalize()
                            existing[site] = row[i]
                except Exception as e:
                    print("[DB FETCH ERROR]", e)

                for site, found in results.items():
                    if existing.get(site) == "Found":
                        final_results[site] = True
                    else:
                        final_results[site] = found
            else:
                final_results = results

            try:
                update_email_info(email, final_results)
            except Exception as e:
                print("[DB ERROR] Could not update DB:", e)

            for site, found in final_results.items():
                color = "green" if found else "red"
                text = f"{site}: {'Found' if found else 'Not Found'}"
                label = tk.Label(self.result_frame, text=text, font=("Helvetica", 12), fg=color, bg="#1A2A2A")
                label.pack(pady=5)

        self.run_async_check(email, show_results, check_only_not_found=not force_all)
