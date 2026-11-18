import tkinter as tk
from tkinter import messagebox

class AdminPage(tk.Frame):
    def __init__(self, parent, go_back_to):
        super().__init__(parent, bg="#1A2A2A")

        self.go_back_to = go_back_to
        self.parent = parent

        ascii_title = r"""
    _    ____  __  __ ___ _   _ _____ ___   ___  _     ____  
   / \  |  _ \|  \/  |_ _| \ | |_   _/ _ \ / _ \| |   / ___| 
  / _ \ | | | | |\/| || ||  \| | | || | | | | | | |   \___ \ 
 / ___ \| |_| | |  | || || |\  | | || |_| | |_| | |___ ___) |
/_/   \_|____/|_|  |_|___|_| \_| |_| \___/ \___/|_____|____/ 
        """

        tk.Label(self, text=ascii_title, font=("Courier", 10), fg="#3CC4BF", bg="#1A2A2A").pack(pady=20)

        from admintools.databaseinterface import DatabasePage

        tk.Button(
            self, text="View Database",
            font=("Helvetica", 14), fg="#6DD3CE", bg="#2E4A2A",
            activeforeground="#1A2A2A", activebackground="#3CC4BF",
            relief="ridge", width=20, height=2,
            command=lambda: parent.show(lambda p: DatabasePage(p, go_back_to=lambda pp: AdminPage(pp, go_back_to=self.go_back_to)))
        ).pack(pady=10)

        from admintools.reportinterface import ReportPage
        tk.Button(
            self, text="Create OSINT report",
            font=("Helvetica", 14), fg="#6DD3CE", bg="#2E4A2A",
            activeforeground="#1A2A2A", activebackground="#3CC4BF",
            relief="ridge", width=20, height=2,
            command=lambda: parent.show(lambda p: ReportPage(p, go_back_to=lambda pp: AdminPage(pp, go_back_to=self.go_back_to)))
        ).pack(pady=10)

        tk.Button(
            self, text="Back",
            command=lambda: parent.show(self.go_back_to),
            font=("Helvetica", 12), fg="#6DD3CE", bg="#2E4A2A",
            activeforeground="#1A2A2A", activebackground="#3CC4BF",
            relief="ridge", width=20, height=2
        ).pack(pady=10)
