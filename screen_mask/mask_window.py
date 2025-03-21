import tkinter as tk
from screeninfo import Monitor
import logging


class MaskWindow:

    def __init__(self, root: tk.Tk, monitor: Monitor):
        self.window = tk.Toplevel(root)
        self.window.withdraw()
        self.window.attributes("-alpha", 1.0, "-topmost", True)
        self.window.overrideredirect(True)
        self.window.configure(bg="black")
        self.window.geometry(
            f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
        )

    def show(self):
        self.window.deiconify() if self.window.winfo_exists() else None

    def hide(self):
        self.window.withdraw() if self.window.winfo_exists() else None

    def destroy(self):
        self.window.destroy() if self.window.winfo_exists() else None

    def set_opacity(self, value: float):
        self.window.attributes("-alpha", value) if self.window.winfo_exists() else None
