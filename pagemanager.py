import customtkinter as ctk

class PageManager(ctk.CTkFrame):
    def __init__(self, root):
        super().__init__(root)
        self.pack(fill="both", expand=True)
        self.frames = {}
        self.current_page = None  # 👈 Add this
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def show(self, page_class):
        frame = self.frames.get(page_class)
        if frame is None:
            frame = page_class(self)
            self.frames[page_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()
        self.current_page = frame  # 👈 Track the active page
