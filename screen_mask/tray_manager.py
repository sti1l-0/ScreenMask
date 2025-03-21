import pystray
from PIL import Image
from typing import Callable, Dict
from screeninfo import Monitor
import os
import queue
import threading
import logging


class TrayManager:
    def __init__(
        self,
        monitors: list[Monitor],
        toggle_callback: Callable[[int], None],
        quit_callback: Callable[[], None],
        get_monitor_state: Callable[[int], bool],
        set_opacity_callback: Callable[[float], float],
    ):
        self.monitors = monitors
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
        self.icon = self.create_tray_icon()

    def create_opacity_menu(self):
        """创建透明度子菜单"""
        return pystray.Menu(
            *[
                pystray.MenuItem(
                    text,
                    self.create_opacity_callback(value),
                    checked=self.create_opacity_checked_callback(value),
                    radio=True,  # 使用单选模式
                )
                for text, value in self.opacity_levels.items()
            ]
        )

    def create_opacity_callback(self, value: float) -> Callable:
        """创建透明度设置回调"""

        def callback(icon, item):
            # 将命令放入队列而不是直接执行
            self.command_queue.put(("set_opacity", value))

        return callback

    def create_opacity_checked_callback(self, value: float) -> Callable:
        """创建透明度选中状态回调"""

        def checked(item):
            current_opacity = self.set_opacity_callback(None)  # 获取当前透明度
            return abs(current_opacity - value) < 0.01  # 浮点数比较

        return checked

    def create_tray_icon(self) -> pystray.Icon:
        """创建托盘图标"""
        # 创建完整菜单
        menu_items = []

        # 添加显示器选项（一级菜单）
        for i, monitor in enumerate(self.monitors):
            menu_items.append(
                pystray.MenuItem(
                    f"显示器 {i+1} ({monitor.width}x{monitor.height})",
                    self.create_monitor_callback(i),
                    checked=self.create_monitor_checked_callback(i),
                )
            )

        # 添加分隔线
        menu_items.append(pystray.Menu.SEPARATOR)

        # 添加透明度子菜单
        menu_items.append(
            pystray.MenuItem(
                "透明度设置",
                pystray.Menu(
                    *[
                        pystray.MenuItem(
                            text,
                            self.create_opacity_callback(value),
                            checked=self.create_opacity_checked_callback(value),
                            radio=True,
                        )
                        for text, value in self.opacity_levels.items()
                    ]
                ),
            )
        )

        # 添加分隔线
        menu_items.append(pystray.Menu.SEPARATOR)

        # 添加退出选项
        menu_items.append(pystray.MenuItem("退出", self.quit_callback))

        # 加载图标文件
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "icons", "monitor.ico"
        )
        if not os.path.exists(icon_path):
            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "icons", "monitor.png"
            )

        if not os.path.exists(icon_path):
            icon_image = Image.new("RGB", (64, 64), "black")
        else:
            icon_image = Image.open(icon_path)

        return pystray.Icon(
            "screen_mask", icon_image, "屏幕遮罩", menu=pystray.Menu(*menu_items)
        )

    def create_monitor_callback(self, index: int) -> Callable:
        """创建显示器切换回调"""

        def callback(icon, item):
            # 将命令放入队列而不是直接执行
            self.command_queue.put(("toggle_monitor", index))

        return callback

    def create_monitor_checked_callback(self, index: int) -> Callable:
        """创建显示器状态检查回调"""

        def checked(item):
            return self.get_monitor_state(index)

        return checked

    def process_commands(self):
        """处理命令队列"""
        while True:
            try:
                command, value = self.command_queue.get(timeout=0.1)
                if command == "toggle_monitor":
                    self.toggle_callback(value)
                elif command == "set_opacity":
                    self.set_opacity_callback(value)
                elif command == "quit":
                    break
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"处理命令时出错: {str(e)}")

    def run(self):
        """运行托盘图标"""
        # 启动命令处理线程
        command_thread = threading.Thread(target=self.process_commands)
        command_thread.daemon = True
        command_thread.start()

        # 运行托盘图标
        self.icon.run()

    def stop(self):
        """停止托盘图标"""
        self.command_queue.put(("quit", None))
        if hasattr(self, "icon"):
            self.icon.stop()
