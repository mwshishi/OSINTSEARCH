import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import re

class DatabasePage(tk.Frame):
    def __init__(self, parent, go_back_to):
        super().__init__(parent, bg="#1A2A2A")
        self.parent = parent
        self.go_back_to = go_back_to
        self.viewing_table = False
        self.show_table_list()

    def get_connection(self):
        return psycopg2.connect(
            host="localhost",
            database="osintSearchDB",
            user="postgres",
            password="admin",
            port="5432"
        )

    def fetch_tables(self):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return tables
        except Exception as e:
            return [f"Error: {e}"]

    def fetch_table_data(self, table):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()
        return colnames, rows

    def update_cell(self, table, column, new_value, row_id):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            if "email" in column:
                if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", new_value):
                    raise ValueError("Invalid email format")
            cur.execute(f"UPDATE {table} SET {column} = %s WHERE {column} IS DISTINCT FROM %s AND {table}_id = %s", (new_value, new_value, row_id))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Update Error", str(e))

    def show_table_data(self, table):
        self.viewing_table = True

        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text=f"Viewing: {table}", font=("Helvetica", 14, "bold"), fg="#3CC4BF", bg="#1A2A2A")
        label.pack(pady=10)

        frame = tk.Frame(self, bg="#1A2A2A")
        frame.pack(fill="both", expand=True)

        cols, rows = self.fetch_table_data(table)
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        tree.pack(side="left", fill="both", expand=True)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in rows:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def on_double_click(event):
            item = tree.selection()[0]
            values = tree.item(item, "values")
            col_idx = int(tree.identify_column(event.x)[1:]) - 1
            col_name = cols[col_idx]

            def submit():
                new_value = entry.get()
                self.update_cell(table, col_name, new_value, values[0])
                tree.set(item, column=col_name, value=new_value)
                top.destroy()

            top = tk.Toplevel(self)
            top.title("Edit Cell")
            tk.Label(top, text=f"Edit {col_name}:").pack(pady=5)
            entry = tk.Entry(top)
            entry.insert(0, values[col_idx])
            entry.pack(pady=5)
            tk.Button(top, text="Save", command=submit).pack(pady=5)

        tree.bind("<Double-1>", on_double_click)

        tk.Button(
            self,
            text="Back",
            command=self.handle_back,
            font=("Helvetica", 12), fg="#6DD3CE", bg="#2E4A42",
            activeforeground="#1A2A2A", activebackground="#3CC4BF",
            relief="ridge", width=20, height=2
        ).pack(pady=10)

    def handle_back(self):
        if self.viewing_table:
            self.show_table_list()
        else:
            self.parent.show(self.go_back_to)




    def show_table_list(self):
        self.viewing_table = False

        for widget in self.winfo_children():
            widget.destroy()

        ascii_title = r"""
 ____        _        _                    
|  _ \  __ _| |_ __ _| |__   ___ _ __ ___  
| | | |/ _` | __/ _` | '_ \ / _ \ '__/ _ \ 
| |_| | (_| | || (_| | | | |  __/ | | (_) |
|____/ \__,_|\__\__,_|_| |_|\___|_|  \___/ 
        """
        label = tk.Label(self, text=ascii_title, font=("Courier", 10), fg="#3CC4BF", bg="#1A2A2A")
        label.pack(pady=20)

        frame = tk.Frame(self, bg="#1A2A2A")
        frame.pack(pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, font=("Helvetica", 12), fg="white", bg="#2E4A42",
                             yscrollcommand=scrollbar.set, selectbackground="#3CC4BF")
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        tables = self.fetch_tables()
        for table in tables:
            listbox.insert(tk.END, table)

        def on_select(event):
            if listbox.curselection():
                table = listbox.get(listbox.curselection())
                self.show_table_data(table)

        listbox.bind("<Double-Button-1>", on_select)

        tk.Button(
            self,
            text="Back",
            command=self.handle_back,
            font=("Helvetica", 12), fg="#6DD3CE", bg="#2E4A42",
            activeforeground="#1A2A2A", activebackground="#3CC4BF",
            relief="ridge", width=20, height=2
        ).pack(pady=10)