import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
import psycopg2
from admintools.savereport import save_as_json, save_as_txt, save_as_pdf, get_next_available_name, overwrite_json
import os
import json
from PIL import Image, ImageTk



class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, master, width, height, **kwargs):
        super().__init__(master, **kwargs)
        bg_color = self.cget("fg_color")
        # Canvas with both scrollbars
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg_color, highlightthickness=0)
        vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        # configure scroll region
        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.scrollable_frame.bind("<Configure>", on_configure)

class AttributeBubble(ctk.CTkFrame):
    def __init__(self, master, canvas, parent_bubble, label, status, x, y, value=None):
        super().__init__(master, width=120, height=30, fg_color=self.get_color(status))
        self.canvas = canvas
        self.parent_bubble = parent_bubble
        self.label_text = label
        self.status = status
        self.value = value

        self.label = ctk.CTkLabel(self, text=self.format_text(label, status, value), font=("Helvetica", 10))
        self.label.pack(expand=True, fill="both")

        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)
        self.label.bind("<Double-Button-1>", self.delete_self)

        self._drag_data = {"x": 0, "y": 0}

        self.window_id = self.canvas.create_window(x, y, window=self, anchor="nw")
        self.line_id = self.canvas.create_line(
            self.parent_bubble.canvas.coords(self.parent_bubble.window_id)[0] + self.parent_bubble.winfo_width() / 2,
            self.parent_bubble.canvas.coords(self.parent_bubble.window_id)[1] + self.parent_bubble.winfo_height() / 2,
            x + 60,
            y + 15,
            fill="white",
            width=1
        )

    def get_color(self, status):
        return {"n/a": "#818A05", "found": "#2E8B57", "not found": "#8B0000"}.get(status.lower(), "#818A05")

    def format_text(self, label, status, value=None):
        if self.parent_bubble.type_key == "phone":
            return f"{label}: {value}" if value else label
        return f"[{status.upper()}]: {label}"

    def start_move(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def do_move(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        coords = self.canvas.coords(self.window_id)
        new_x = coords[0] + dx
        new_y = coords[1] + dy

        max_x = self.canvas.winfo_width() - self.winfo_width()
        max_y = self.canvas.winfo_height() - self.winfo_height()
        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        self.canvas.coords(self.window_id, new_x, new_y)
        self.update_line()


    def update_line(self):
        if hasattr(self, 'line_id'):
            main_coords = self.canvas.coords(self.parent_bubble.window_id)
            attr_coords = self.canvas.coords(self.window_id)
            self.canvas.coords(
                self.line_id,
                main_coords[0] + self.parent_bubble.winfo_width() / 2,
                main_coords[1] + self.parent_bubble.winfo_height() / 2,
                attr_coords[0] + self.winfo_width() / 2,
                attr_coords[1] + self.winfo_height() / 2
            )

    def delete_self(self, event=None):
        # remove from canvas
        self.canvas.delete(self.window_id)
        if hasattr(self, 'line_id'):
            self.canvas.delete(self.line_id)

        # remove from parent bookkeeping
        if self.label_text in self.parent_bubble.added_attributes:
            self.parent_bubble.added_attributes.remove(self.label_text)
        if self in self.parent_bubble.attribute_bubbles:
            self.parent_bubble.attribute_bubbles.remove(self)


class DraggableEmail(ctk.CTkFrame):
    existing_labels = set()

    def __init__(self, master, canvas, x=10, y=10, label="test email"):
        super().__init__(master, width=120, height=40, fg_color="#3C7DC4")
        self.canvas = canvas
        self.label_text = label
        self.status = "undefined"
        self.window_id = canvas.create_window(x, y, window=self, anchor="nw")
        self.added_attributes = set()
        self.attribute_bubbles = []
        self.type_key = "email" if "@" in label else ("phone" if label.replace("+", "").isdigit() else "username")

        self.label = ctk.CTkLabel(self, text=label, text_color="black", font=("Helvetica", 12, "bold"))
        self.label.pack(expand=True, fill="both")

        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)
        self.label.bind("<Double-Button-1>", self.open_options_popup)


        # ——— AND ALSO bind the frame itself ———
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>",    self.do_move)


        DraggableEmail.existing_labels.add(label)
        self._drag_data = {"x": 0, "y": 0}

    def start_move(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def move_attributes_with_parent(self, dx, dy):
        for attr_bubble in self.attribute_bubbles:
            coords = self.canvas.coords(attr_bubble.window_id)
            new_x = coords[0] + dx
            new_y = coords[1] + dy
            self.canvas.coords(attr_bubble.window_id, new_x, new_y)
            attr_bubble.update_line()

    def do_move(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        coords = self.canvas.coords(self.window_id)
        new_x = coords[0] + dx
        new_y = coords[1] + dy

        max_x = self.canvas.winfo_width() - self.winfo_width()
        max_y = self.canvas.winfo_height() - self.winfo_height()
        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        dx_final = new_x - coords[0]
        dy_final = new_y - coords[1]

        self.canvas.coords(self.window_id, new_x, new_y)
        self.move_attributes_with_parent(dx_final, dy_final)


    def open_options_popup(self, event):
        x_root = self.winfo_rootx() + event.x
        y_root = self.winfo_rooty() + event.y

        popup = ctk.CTkToplevel(self)
        popup.geometry(f"200x200+{x_root}+{y_root}")
        popup.title("Options")
        popup.attributes("-topmost", True)

        def delete():
            # Delete all attached attribute bubbles first
            for attr_bubble in self.attribute_bubbles:
                self.canvas.delete(attr_bubble.window_id)
                if hasattr(attr_bubble, 'line_id'):
                    self.canvas.delete(attr_bubble.line_id)
            self.attribute_bubbles.clear()
            self.added_attributes.clear()

            # Now delete the main bubble
            self.canvas.delete(self.window_id)
            self.destroy()
            DraggableEmail.existing_labels.discard(self.label_text)
            popup.destroy()


        def set_status(color, status):
            self.configure(fg_color=color)
            self.status = status
            popup.destroy()

        ctk.CTkButton(popup, text="Delete", fg_color="red", command=delete).pack(pady=(10, 5), fill="x", padx=10)
        ctk.CTkLabel(popup, text="Set Trust Status:").pack(pady=(5, 2))
        ctk.CTkButton(popup, text="Confirmed", text_color="green", command=lambda: set_status("#2E8B57", "confirmed")).pack(fill="x", padx=10)
        ctk.CTkButton(popup, text="Possible", text_color="yellow", command=lambda: set_status("#818A05", "possible")).pack(fill="x", padx=10)
        ctk.CTkButton(popup, text="Undefined", text_color="blue", command=lambda: set_status("#3C7DC4", "undefined")).pack(fill="x", padx=10)
        ctk.CTkButton(popup, text="Add Attribute", command=lambda: self.open_attribute_selector(popup)).pack(pady=(10, 5), fill="x", padx=10)

        popup.grab_set()

    def open_attribute_selector(self, parent_popup):
        parent_popup.destroy()
        attr_popup = ctk.CTkToplevel(self)
        attr_popup.title("Select Attribute")
        attr_popup.geometry("300x400")
        attr_popup.attributes("-topmost", True)

        canvas = tk.Canvas(attr_popup, borderwidth=0, background="#1E1E1E")
        frame = tk.Frame(canvas, background="#1E1E1E")
        vsb = tk.Scrollbar(attr_popup, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        table = f"{self.type_key}_info"
        exclude_col = self.type_key

        try:
            conn = psycopg2.connect(
                host="localhost",
                database="osintSearchDB",
                user="postgres",
                password="admin",
                port="5432"
            )
            cur = conn.cursor()
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table,))
            all_cols = [row[0] for row in cur.fetchall() if row[0] != exclude_col]

            cur.execute(f"SELECT * FROM {table} WHERE {exclude_col} = %s", (self.label_text,))
            result = cur.fetchone()
            col_names = [desc[0] for desc in cur.description]
            result_dict = dict(zip(col_names, result)) if result else {}

            spacing = 30
            x, y = 20, 20 + len(self.attribute_bubbles) * spacing

                        # Add All button
            def add_all_attributes():
                for col in all_cols:
                    if col in self.added_attributes:
                        continue
                    raw_value = result_dict.get(col, "")
                    value_display = str(raw_value) if raw_value is not None else ""
                    if self.type_key == "phone":
                        status = "found"
                    else:
                        lowered = value_display.strip().lower()
                        if lowered == "found":
                            status = "found"
                        elif lowered == "not found":
                            status = "not found"
                        else:
                            status = "n/a"

                    self.add_attribute(col, status, attr_popup, value_display)
                attr_popup.destroy()

            ctk.CTkButton(frame, text="➕ Add All Attributes", fg_color="#3C7DC4", command=add_all_attributes).pack(pady=(0, 10), fill="x")

            for col in all_cols:
                if col in self.added_attributes:
                    continue
                raw_value = result_dict.get(col, "")
                value_display = str(raw_value) if raw_value is not None else ""
                if self.type_key == "phone":
                    status = "found"
                else:
                    lowered = value_display.strip().lower()
                    if lowered == "found":
                        status = "found"
                    elif lowered == "not found":
                        status = "not found"
                    else:
                        status = "n/a"

                btn = ctk.CTkButton(
                    frame,
                    text=f"{col}: {value_display}",
                    command=lambda c=col, s=status, v=value_display: self.add_attribute(c, s, attr_popup, v)
                )

                btn.pack(pady=2, fill="x")

            cur.close()
            conn.close()
        except Exception as e:
            tk.Label(frame, text=f"DB Error: {e}", fg="red", bg="#1E1E1E").pack()

        attr_popup.grab_set()

    def add_attribute(self, attr_name, status, popup, value=None):
        if attr_name not in self.added_attributes:
            coords = self.canvas.coords(self.window_id)
            attr_bubble = AttributeBubble(
                self.canvas, self.canvas, self, attr_name, status,
                coords[0] + 140, coords[1] + 30 + len(self.attribute_bubbles) * 40,
                value=value
            )
            self.attribute_bubbles.append(attr_bubble)
            self.added_attributes.add(attr_name)
        popup.destroy()


class ReportPage(ctk.CTkFrame):
    def __init__(self, parent, go_back_to=None):
        super().__init__(parent, fg_color="#0B0F1A")
        self.parent = parent

        self.go_back_to = go_back_to
        self.photo_folder = None
        self.photo_items = []
        self.photo_thumbs = []

        ctk.CTkLabel(self, text="Report Interface", font=("Helvetica", 20, "bold"), text_color="#3CC4BF").pack(pady=20)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Add Email", command=lambda: self.open_selector("email")).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Add Phone", command=lambda: self.open_selector("phone")).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Add Username", command=lambda: self.open_selector("username")).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Add Photo Folder", command=self.open_photo_folder).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Save Report", command=self.open_save_popup).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Load Report", fg_color="green", command=self.load_report).pack(side="left", padx=10)
        if self.go_back_to:
            ctk.CTkButton(button_frame, text="Back", command=self.confirm_back, fg_color="#2E4A2A", hover_color="#3CC4BF").pack(side="left", padx=10)


        # Main canvas for bubbles
        # Main canvas (no fixed width) to expand when no photos
        self.canvas = tk.Canvas(self, bg="#16202E")
        self.canvas.pack(side="left", pady=20, expand=True, fill="both")

        # Container for photos on right
        self.photos_frame = None

        

    def confirm_back(self):
        if self.has_unsaved_bubbles():
            result = tk.messagebox.askyesno(
                "Unsaved Report", "You have an unsaved report in progress. If you go back, the report will be invalidated. Continue?"
            )
            if not result:
                return
            self.clear_all_bubbles()
        self.parent.show(self.go_back_to)

    def open_photo_folder(self):
        folder = tk.filedialog.askdirectory(initialdir=os.path.join(os.getcwd(), "photo"),
                                             title="Select Photo Subfolder")
        if not folder: return
        self.photo_folder = os.path.basename(folder)
        entries = []
        for fname in sorted(os.listdir(folder)):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                path = os.path.join(folder, fname)
                base = os.path.splitext(fname)[0]
                txt_path = os.path.join(folder, base + '.txt')
                desc, src = '', ''
                if os.path.exists(txt_path):
                    lines = open(txt_path).read().splitlines()
                    if lines: desc = lines[0].replace('Description:', '').strip()
                    if len(lines) > 1: src = lines[1].replace('Source:', '').strip()
                entries.append((path, desc, src))
        popup = ctk.CTkToplevel(self)
        popup.title("Preview Photos")
        popup.geometry("900x500")  # wider
        sf = ScrollableFrame(popup, width=880, height=420, fg_color="#0B0F1A")
        sf.pack(padx=10, pady=10)
        for path, desc, src in entries:
            frame = ctk.CTkFrame(sf.scrollable_frame, fg_color="#1E1E1E")
            frame.pack(fill="x", pady=5)
            img = Image.open(path)
            img.thumbnail((160, 160))  # larger
            tk_img = ImageTk.PhotoImage(img)
            tk.Label(frame, image=tk_img).pack(side="left", padx=5)
            self.photo_thumbs.append(tk_img)
            ctk.CTkLabel(frame, text=f"{desc}\nSource: {src}", anchor="w", justify="left").pack(side="left", padx=5)
        ctk.CTkButton(popup, text="Add All Photos", command=lambda: (self.add_all_photos(entries), popup.destroy())).pack(pady=5)
        popup.grab_set()

    def add_all_photos(self, entries):
        if self.photos_frame: self.photos_frame.destroy()
        self.photos_frame = ScrollableFrame(self, width=400, height=450, fg_color="#16202E")  # wider
        self.photos_frame.pack(side="right", pady=20, fill="both")
        self.photo_thumbs.clear()
        for path, desc, src in entries:
            frame = ctk.CTkFrame(self.photos_frame.scrollable_frame, fg_color="#1E1E1E")
            frame.pack(fill="x", pady=5)
            img = Image.open(path)
            img.thumbnail((160, 160))  # larger
            tk_img = ImageTk.PhotoImage(img)
            tk.Label(frame, image=tk_img).pack(side="left", padx=5)
            self.photo_thumbs.append(tk_img)
            ctk.CTkLabel(frame, text=f"{desc}\nSource: {src}", anchor="w", justify="left").pack(side="left", padx=5)
        self.photo_items = entries

    def add_email(self, label):
        self.add_draggable(label)

    def add_phone(self, label):
        self.add_draggable(label)

    def add_username(self, label):
        self.add_draggable(label)

    def add_draggable(self, label):
        if label in DraggableEmail.existing_labels:
            popup = ctk.CTkToplevel(self)
            popup.geometry("350x120")
            center_popup(popup, self.winfo_toplevel())

            popup.title("Duplicate Entry")
            ctk.CTkLabel(popup, text=f"{label} already added. Add again?").pack(pady=10)

            def confirm():
                DraggableEmail(self, self.canvas, label=label)
                popup.destroy()

            def cancel():
                popup.destroy()

            ctk.CTkButton(popup, text="Yes", command=confirm).pack(side="left", padx=20, pady=10)
            ctk.CTkButton(popup, text="No", command=cancel).pack(side="right", padx=20, pady=10)
            popup.grab_set()
        else:
            DraggableEmail(self, self.canvas, label=label)

    def open_selector(self, mode):
        popup = tk.Toplevel(self)
        popup.title(f"Select {mode.title()}")
        popup.geometry("600x400")
        self.update_idletasks()
        app_x = self.winfo_rootx()
        app_y = self.winfo_rooty()
        app_w = self.winfo_width()
        app_h = self.winfo_height()

        popup_x = app_x + (app_w // 2) - 300
        popup_y = app_y + (app_h // 2) - 200
        popup.geometry(f"600x400+{popup_x}+{popup_y}")
        popup.configure(bg="#0B0F1A")

        search_frame = tk.Frame(popup, bg="#0B0F1A")
        search_frame.pack(pady=10)

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side="left", padx=10)

        tree = ttk.Treeview(popup, columns=(mode,), show="headings")
        tree.heading(mode, text=mode.title())
        tree.pack(fill="both", expand=True)

        def update_tree(query=""):
            for i in tree.get_children():
                tree.delete(i)

            sql = {
                "email": "SELECT email FROM email_info WHERE email ILIKE %s;",
                "phone": "SELECT phone FROM phone_info WHERE phone ILIKE %s;",
                "username": "SELECT username FROM username_info WHERE username ILIKE %s;"
            }

            try:
                conn = psycopg2.connect(
                    host="localhost",
                    database="osintSearchDB",
                    user="postgres",
                    password="admin",
                    port="5432"
                )
                cur = conn.cursor()
                cur.execute(sql[mode], (f"%{query}%",))
                for row in cur.fetchall():
                    tree.insert("", "end", values=(row[0],))
                cur.close()
                conn.close()
            except Exception as e:
                tk.Label(popup, text=f"DB Error: {e}", fg="red", bg="#0B0F1A").pack()

        search_var.trace_add("write", lambda *_: update_tree(search_var.get()))
        update_tree()

        def on_select(event):
            selected = tree.focus()
            if selected:
                values = tree.item(selected, "values")
                if values:
                    self.add_draggable(values[0])
                    popup.destroy()

        tree.bind("<Double-1>", on_select)
    
    def load_report(self):
        folder_selected = tk.filedialog.askdirectory(initialdir="OSINT_REPORTS", title="Select a report folder")
        if not folder_selected: return

        
        if self.has_unsaved_bubbles():
            result = tk.messagebox.askyesno(
                "Overwrite Current Report?",
                "Loading a report will invalidate the current report. Continue?"
            )
            if not result:
                return
            self.clear_all_bubbles()

        json_path = os.path.join(folder_selected, "report.json")

        if not os.path.exists(json_path):
            tk.messagebox.showerror("Error", "Not a valid report to load (missing .json)")
            return
        try:
            with open(os.path.join(folder_selected, 'report.json'), 'r') as f:
                data = json.load(f)

            if "bubbles" not in data:
                raise ValueError("Invalid report structure")
            self.clear_all_bubbles()
            for b in data["bubbles"]:
                main = DraggableEmail(self, self.canvas, label=b["label"])
                main.type_key = b.get("type", "email")
                main.configure(fg_color=b.get("color", "#3C7DC4"))
                self.canvas.coords(main.window_id, b["x"], b["y"])
                for attr in b["attributes"]:
                    ab = AttributeBubble(
                        self.canvas, self.canvas, main,
                        attr["name"], attr["status"],
                        attr["x"], attr["y"],
                        value=attr.get("value")
                    )
                    ab.configure(fg_color=attr.get("color", "#818A05"))
                    main.attribute_bubbles.append(ab)
                    main.added_attributes.add(attr["name"])
            
            pf = data.get('photo_folder')
            if pf:
                entries = []
                src_dir = os.path.join(folder_selected, pf)
                for fname in sorted(os.listdir(src_dir)):
                    if fname.lower().endswith(('.png','.jpg','.jpeg','.gif')):
                        path = os.path.join(src_dir, fname)
                        base = os.path.splitext(fname)[0]
                        txt_path = os.path.join(src_dir, base + '.txt')
                        desc, src_txt = '', ''
                        if os.path.exists(txt_path):
                            with open(txt_path, 'r') as f2:
                                lines = f2.read().splitlines()
                                if lines: desc = lines[0].replace('Description:', '').strip()
                                if len(lines) > 1: src_txt = lines[1].replace('Source:', '').strip()
                        entries.append((path, desc, src_txt))
                self.add_all_photos(entries)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Invalid report: {e}")

    def open_save_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Save Report")
        popup.geometry("300x350")
        popup.attributes("-topmost", True)

        selected_format = tk.StringVar(value="json")
        include_txt = tk.BooleanVar(value=False)
        include_pdf = tk.BooleanVar(value=False)
        report_name = tk.StringVar()

        ctk.CTkLabel(popup, text="Report Name:").pack(pady=(10, 2), anchor="w", padx=20)
        name_entry = ctk.CTkEntry(popup, textvariable=report_name)
        name_entry.pack(pady=(0, 10), fill="x", padx=20)

        ctk.CTkLabel(popup, text="Select formats:").pack(anchor="w", padx=20)

        # JSON is mandatory (always saved)
        ctk.CTkRadioButton(
            popup,
            text=".json (always)",
            variable=selected_format,
            value="json",
            state="disabled"
        ).pack(anchor="w", padx=20)

        # Let the user choose .txt and/or .pdf
        ctk.CTkCheckBox(popup, text=".txt", variable=include_txt).pack(anchor="w", padx=20)
        ctk.CTkCheckBox(popup, text=".pdf", variable=include_pdf).pack(anchor="w", padx=20)

        def collect_report_data():
            """
            Gathers all bubble data + the chosen photo_folder (if any).
            """
            bubbles = []
            for widget in self.winfo_children():
                if isinstance(widget, DraggableEmail):
                    bubble_dict = {
                        "label": widget.label_text,
                        "type": widget.type_key,
                        "color": widget.cget("fg_color"),
                        "x": self.canvas.coords(widget.window_id)[0],
                        "y": self.canvas.coords(widget.window_id)[1],
                        "attributes": []
                    }
                    for ab in widget.attribute_bubbles:
                        bubble_dict["attributes"].append({
                            "name": ab.label_text,
                            "status": ab.status,
                            "value": ab.value,
                            "x": self.canvas.coords(ab.window_id)[0],
                            "y": self.canvas.coords(ab.window_id)[1],
                            "color": ab.cget("fg_color")
                        })
                    bubbles.append(bubble_dict)

            result = {
                "name": report_name.get(),
                "bubbles": bubbles
            }
            if self.photo_folder:
                result["photo_folder"] = self.photo_folder
            return result

        def copy_photos_into_report_folder(final_name):
            """
            Copies the entire photo folder from ./photo/<photo_folder>
            into OSINT_REPORTS/<final_name>/<photo_folder>, so that
            save_as_pdf can embed them.
            """
            if not self.photo_folder:
                return

            src_folder = os.path.join(os.getcwd(), "photo", self.photo_folder)
            dst_folder = os.path.join(os.getcwd(), "OSINT_REPORTS", final_name, self.photo_folder)
            os.makedirs(dst_folder, exist_ok=True)

            for fname in os.listdir(src_folder):
                src_path = os.path.join(src_folder, fname)
                dst_path = os.path.join(dst_folder, fname)
                with open(src_path, "rb") as fsrc, open(dst_path, "wb") as fdst:
                    fdst.write(fsrc.read())

        def save_final(final_name):
            """
            After JSON is written, overwrite or copy:
            1) Ensures that photos are copied first.
            2) Optionally writes .txt / .pdf
            3) Destroys the popup.
            """
            data = collect_report_data()

            # 1) We have already created JSON via save_as_json or overwrite_json.
            #    But for a new copy, ensure JSON is present:
            save_as_json(data, final_name)

            # 2) Copy photos BEFORE generating PDF
            copy_photos_into_report_folder(final_name)

            # 3) Now generate .txt and/or .pdf
            if include_txt.get():
                save_as_txt(data, final_name)
            if include_pdf.get():
                save_as_pdf(data, final_name)

            popup.destroy()

        def confirm_existing():
            """
            If the folder already exists, let the user choose Overwrite vs. Save a Copy.
            """
            overwrite_popup = ctk.CTkToplevel(popup)
            overwrite_popup.title("Report Exists")
            overwrite_popup.geometry("280x130")
            ctk.CTkLabel(overwrite_popup, text=f"Report '{report_name.get()}' already exists.").pack(pady=10)

            def do_overwrite():
                # Since the folder exists, collect data and overwrite:
                data = collect_report_data()
                overwrite_json(data, report_name.get())

                # Copy photos first, then regenerate PDF/TXT if requested:
                copy_photos_into_report_folder(report_name.get())

                if include_txt.get():
                    save_as_txt(data, report_name.get())
                if include_pdf.get():
                    save_as_pdf(data, report_name.get())

                overwrite_popup.destroy()
                popup.destroy()

            def do_save_copy():
                new_name = get_next_available_name(report_name.get())
                # Create a fresh folder + JSON inside it, then copy photos / txt / pdf
                save_final(new_name)
                overwrite_popup.destroy()

            ctk.CTkButton(
                overwrite_popup,
                text="Overwrite",
                command=do_overwrite
            ).pack(pady=5, fill="x", padx=20)

            ctk.CTkButton(
                overwrite_popup,
                text="Save a Copy",
                command=do_save_copy
            ).pack(pady=5, fill="x", padx=20)

            overwrite_popup.grab_set()

        def perform_save():
            """
            Called when the user clicks “Save” for the very first time.
            If OSINT_REPORTS/<name> does not exist, save_as_json returns "saved".
            If it does exist, save_as_json returns "exists" → show confirm_existing().
            """
            name = report_name.get().strip()
            # Basic name validation
            if not name or any(c in r'<>:"/\\|?*' for c in name):
                tk.messagebox.showerror("Invalid Name", "Please enter a valid report name.")
                return

            data = collect_report_data()
            result = save_as_json(data, name)
            if result == "exists":
                # Let the user choose Overwrite or Save a Copy
                confirm_existing()
            else:
                # Newly created folder. Now:
                # 1) Copy photos into the newly created folder
                copy_photos_into_report_folder(name)

                # 2) Write .txt/.pdf if requested
                if include_txt.get():
                    save_as_txt(data, name)
                if include_pdf.get():
                    save_as_pdf(data, name)

                popup.destroy()

        # Finally, add the “Save” button
        ctk.CTkButton(popup, text="Save", command=perform_save).pack(pady=20, fill="x", padx=20)
        popup.grab_set()
    
    def has_unsaved_bubbles(self): 
        return any(isinstance(widget, DraggableEmail) for widget in self.winfo_children())
    
    def clear_all_bubbles(self):
        for widget in list(self.winfo_children()):
            if isinstance(widget, DraggableEmail):
                for ab in widget.attribute_bubbles:
                    self.canvas.delete(ab.window_id)
                    if hasattr(ab, 'line_id'):
                        self.canvas.delete(ab.line_id)
                widget.attribute_bubbles.clear()
                widget.added_attributes.clear()
                self.canvas.delete(widget.window_id)
                widget.destroy()
        DraggableEmail.existing_labels.clear()
        if self.photos_frame:
            self.photos_frame.destroy()
            self.photos_frame = None
        self.photo_items = []





def center_popup(popup, parent):
    popup.update_idletasks()
    parent.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (popup.winfo_width() // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")
