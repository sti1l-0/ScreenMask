import pystray
from PIL import Image
import os
from typing import Callable, List
import queue
import threading
import logging
from screeninfo import Monitor


class TrayManager:

    def __init__(
        self,
        monitors: List[Monitor],
        toggle_callback: Callable[[int], None],
        quit_callback: Callable[[], None],
        get_monitor_state: Callable[[int], bool],
        set_opacity_callback: Callable[[float], float],
    ):
        self.toggle_callback = toggle_callback
        self.quit_callback = quit_callback
        self.get_monitor_state = get_monitor_state
        self.set_opacity_callback = set_opacity_callback
        self.command_queue = queue.Queue()
        self.opacity_levels = {
            "不透明 (100%)": 1.0,
            "稍透明 (75%)": 0.75,
            "半透明 (50%)": 0.5,
            "较透明 (25%)": 0.25,
            "全透明 (0%)": 0.0,
        }

        menu_items = []

        for i, m in enumerate(monitors):
            menu_items.append(
                pystray.MenuItem(
                    f"显示器 {i+1} ({m.width}x{m.height})",
                    self.create_monitor_callback(i),
                    checked=self.create_monitor_checked_callback(i),
                )
            )

        menu_items.append(pystray.Menu.SEPARATOR)

        opacity_menu_items = []
        for text, value in self.opacity_levels.items():
            opacity_menu_items.append(
                pystray.MenuItem(
                    text,
                    self.create_opacity_callback(value),
                    checked=self.create_opacity_checked_callback(value),
                    radio=True,
                )
            )

        menu_items.append(
            pystray.MenuItem("透明度设置", pystray.Menu(*opacity_menu_items))
        )

        menu_items.append(pystray.Menu.SEPARATOR)
        menu_items.append(pystray.MenuItem("退出", self.quit_callback))

        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "icons", "monitor.ico"
        )
        if not os.path.exists(icon_path):
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "icons", "monitor.png"
            )
        icon_image = (
            Image.open(icon_path)
            if os.path.exists(icon_path)
            else Image.new("RGB", (64, 64), "black")
        )
        self.icon = pystray.Icon(
            "screen_mask", icon_image, "屏幕遮罩", menu=pystray.Menu(*menu_items)
        )

    def create_monitor_callback(self, index: int) -> Callable:
        def callback(icon, item):
            self.command_queue.put(("toggle_monitor", index))

        return callback

    def create_monitor_checked_callback(self, index: int) -> Callable:

        def checked(item):
            return self.get_monitor_state(index)

        return checked

    def create_opacity_callback(self, value: float) -> Callable:
        def callback(icon, item):
            self.command_queue.put(("set_opacity", value))

        return callback

    def create_opacity_checked_callback(self, value: float) -> Callable:
        def checked(item):
            current = self.set_opacity_callback(None)
            return abs(current - value) < 0.01

        return checked

    def process_commands(self):
        """处理命令队列"""
        while True:
            try:
                cmd, val = self.command_queue.get(timeout=0.1)
                if cmd == "toggle_monitor":
                    self.toggle_callback(val)
                elif cmd == "set_opacity":
                    self.set_opacity_callback(val)
                elif cmd == "quit":
                    break
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"命令处理错误: {str(e)}")

    def run(self):
        """运行托盘图标"""
        threading.Thread(target=self.process_commands, daemon=True).start()
        self.icon.run()

    def stop(self):
        """停止托盘图标"""
        self.command_queue.put(("quit", None))
        self.icon.stop()
