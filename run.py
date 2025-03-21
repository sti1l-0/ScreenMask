import tkinter as tk
from tkinter import messagebox
import traceback
import sys
from screen_mask import ScreenMaskApp


def main():
    try:
        app = ScreenMaskApp()
        app.run()
    except Exception as e:
        error_info = traceback.format_exc()
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "错误", f"程序发生致命错误：\n{str(e)}\n\n详细信息：\n{error_info}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
