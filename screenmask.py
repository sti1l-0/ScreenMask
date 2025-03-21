import tkinter as tk
from tkinter import messagebox
from screeninfo import get_monitors
import pystray
from PIL import Image
import threading
import time
import sys
import traceback
import win32api


class ScreenMask:
    def __init__(self):
        try:
            # 获取所有显示器
            self.monitors = get_monitors()
            if not self.monitors:
                raise Exception("未检测到任何显示器")

            # 初始化变量
            self.monitor_states = {i: False for i in range(len(self.monitors))}
            self.mask_windows = {}
            self.running = True

            # 创建主窗口
            self.root = tk.Tk()
            self.root.withdraw()

            # 创建托盘图标
            self.create_tray_icon()

            # 启动鼠标检测
            self.check_mouse_position()

        except Exception as e:
            self.show_error_and_exit(f"初始化失败：{str(e)}")

    def create_mask_window(self, monitor):
        """创建遮罩窗口"""
        window = tk.Toplevel(self.root)
        window.withdraw()  # 初始时隐藏窗口
        window.attributes("-alpha", 0.9)
        window.attributes("-topmost", True)
        window.overrideredirect(True)  # 无边框窗口
        window.configure(bg="black")

        # 设置窗口大小和位置
        geometry = f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}"
        window.geometry(geometry)

        return window

    def check_mouse_position(self):
        """检查鼠标位置并更新遮罩窗口"""
        if not self.running:
            return

        try:
            mouse_x, mouse_y = win32api.GetCursorPos()

            for i, monitor in enumerate(self.monitors):
                if self.monitor_states[i]:
                    in_monitor = (
                        monitor.x <= mouse_x < monitor.x + monitor.width
                        and monitor.y <= mouse_y < monitor.y + monitor.height
                    )

                    if i in self.mask_windows:
                        if in_monitor:
                            self.mask_windows[i].withdraw()
                        else:
                            self.mask_windows[i].deiconify()

            # 安排下一次检查
            self.root.after(100, self.check_mouse_position)

        except Exception as e:
            self.show_error_and_exit(f"鼠标位置检测错误：{str(e)}")

    def toggle_monitor(self, monitor_index):
        """切换显示器遮罩状态"""
        try:
            self.monitor_states[monitor_index] = not self.monitor_states[monitor_index]

            if self.monitor_states[monitor_index]:
                # 在主线程中创建窗口
                if monitor_index not in self.mask_windows:
                    self.root.after(0, self.create_and_store_window, monitor_index)
            else:
                # 在主线程中销毁窗口
                if monitor_index in self.mask_windows:
                    self.root.after(0, self.destroy_window, monitor_index)

        except Exception as e:
            self.show_error_and_exit(f"切换显示器状态失败：{str(e)}")

    def create_and_store_window(self, monitor_index):
        """在主线程中创建并存储窗口"""
        self.mask_windows[monitor_index] = self.create_mask_window(
            self.monitors[monitor_index]
        )

    def destroy_window(self, monitor_index):
        """在主线程中销毁窗口"""
        if monitor_index in self.mask_windows:
            self.mask_windows[monitor_index].destroy()
            del self.mask_windows[monitor_index]

    def create_tray_icon(self):
        """创建托盘图标"""
        menu_items = []
        for i, monitor in enumerate(self.monitors):
            menu_items.append(
                pystray.MenuItem(
                    f"显示器 {i+1} ({monitor.width}x{monitor.height})",
                    self.create_monitor_callback(i),
                    checked=self.create_monitor_checked_callback(i),
                )
            )
        menu_items.append(pystray.MenuItem("退出", self.quit_app))

        image = Image.new("RGB", (64, 64), "black")
        self.icon = pystray.Icon(
            "screen_mask", image, "屏幕遮罩", menu=pystray.Menu(*menu_items)
        )

    def create_monitor_callback(self, index):
        def callback(icon, item):
            self.toggle_monitor(index)

        return callback

    def create_monitor_checked_callback(self, index):
        def checked(item):
            return self.monitor_states[index]

        return checked

    def show_error_and_exit(self, error_message):
        """显示错误信息并退出程序"""
        messagebox.showerror("错误", error_message)
        self.quit_app()

    def quit_app(self):
        """退出应用程序"""
        self.running = False
        for window in self.mask_windows.values():
            window.destroy()
        self.root.after(100, self.root.destroy)
        if hasattr(self, "icon"):
            self.icon.stop()

    def run(self):
        """运行应用程序"""
        try:
            # 在新线程中运行托盘图标
            tray_thread = threading.Thread(target=self.icon.run)
            tray_thread.daemon = True
            tray_thread.start()

            # 在主线程中运行主循环
            self.root.mainloop()

        except Exception as e:
            self.show_error_and_exit(f"程序运行错误：{str(e)}")


def main():
    try:
        app = ScreenMask()
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
