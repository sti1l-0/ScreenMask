import tkinter as tk
from tkinter import messagebox
from screeninfo import get_monitors
import threading
import sys
import traceback
from typing import Dict
import logging
import queue
import win32api

from .mask_window import MaskWindow
from .tray_manager import TrayManager
from .mouse_tracker import MouseTracker


class ScreenMaskApp:
    def __init__(self):
        try:
            # 配置日志
            logging.basicConfig(
                level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
            )

            # 初始化线程安全的队列用于窗口操作
            self.window_queue = queue.Queue()

            # 初始化主窗口
            self.root = tk.Tk()
            self.root.withdraw()

            # 获取显示器信息
            self.monitors = get_monitors()
            if not self.monitors:
                raise Exception("未检测到任何显示器")

            # 初始化状态
            self.running = True
            self.monitor_states = {i: False for i in range(len(self.monitors))}
            self.mask_windows: Dict[int, MaskWindow] = {}
            self._lock = threading.Lock()
            self.opacity = 1.0

            # 初始化托盘管理器
            self.tray_manager = TrayManager(
                self.monitors,
                self.toggle_monitor,
                self.quit_app,
                self.get_monitor_state,
                self.set_opacity,
            )

            # 初始化鼠标跟踪器
            self.mouse_tracker = MouseTracker()

            # 启动窗口操作处理
            self.start_window_handler()

            # 启动鼠标位置检测
            self.start_mouse_check()

        except Exception as e:
            logging.error(f"初始化失败: {str(e)}")
            self.show_error_and_exit(f"初始化失败：{str(e)}")

    def get_monitor_state(self, monitor_index: int) -> bool:
        """获取显示器状态"""
        with self._lock:
            return self.monitor_states.get(monitor_index, False)

    def toggle_monitor(self, monitor_index: int):
        """切换显示器遮罩状态"""
        try:
            with self._lock:
                current_state = self.monitor_states[monitor_index]
                self.monitor_states[monitor_index] = not current_state

                if self.monitor_states[monitor_index]:
                    self.window_queue.put(("create", (monitor_index,)))
                else:
                    self.window_queue.put(("destroy", (monitor_index,)))

        except Exception as e:
            logging.error(f"切换显示器状态失败: {str(e)}")

    def set_opacity(self, value: float = None) -> float:
        """设置或获取透明度"""
        try:
            with self._lock:
                if value is not None:
                    self.opacity = value
                    self.window_queue.put(("update_opacity", (value,)))
                return self.opacity
        except Exception as e:
            logging.error(f"设置透明度失败: {str(e)}")
            return self.opacity

    def _create_mask_window(self, monitor_index: int):
        """实际创建遮罩窗口的方法"""
        try:
            if monitor_index not in self.mask_windows:
                window = MaskWindow(self.root, self.monitors[monitor_index])
                window.set_opacity(self.opacity)
                self.mask_windows[monitor_index] = window
        except Exception as e:
            logging.error(f"创建遮罩窗口失败: {str(e)}")

    def _destroy_mask_window(self, monitor_index: int):
        """实际销毁遮罩窗口的方法"""
        try:
            if monitor_index in self.mask_windows:
                self.mask_windows[monitor_index].destroy()
                del self.mask_windows[monitor_index]
        except Exception as e:
            logging.error(f"销毁遮罩窗口失败: {str(e)}")

    def _update_window_opacity(self, value: float):
        """实际更新窗口透明度的方法"""
        try:
            for window in self.mask_windows.values():
                window.set_opacity(value)
        except Exception as e:
            logging.error(f"更新窗口透明度失败: {str(e)}")

    def start_window_handler(self):
        """启动窗口操作处理"""

        def process_window_operations():
            if not self.running:
                return
            try:
                while not self.window_queue.empty():
                    operation, args = self.window_queue.get_nowait()
                    if operation == "create":
                        self._create_mask_window(*args)
                    elif operation == "destroy":
                        self._destroy_mask_window(*args)
                    elif operation == "update_opacity":
                        self._update_window_opacity(*args)
            except Exception as e:
                logging.error(f"处理窗口操作时出错: {str(e)}")
            finally:
                self.root.after(100, process_window_operations)

        self.root.after(100, process_window_operations)

    def check_mouse_position(self):
        """检查鼠标位置并更新遮罩窗口"""
        if not self.running:
            return

        try:
            mouse_pos = win32api.GetCursorPos()

            with self._lock:
                for i, monitor in enumerate(self.monitors):
                    try:
                        if self.monitor_states.get(i, False) and i in self.mask_windows:
                            in_monitor = (
                                monitor.x <= mouse_pos[0] < monitor.x + monitor.width
                                and monitor.y
                                <= mouse_pos[1]
                                < monitor.y + monitor.height
                            )
                            (
                                self.mask_windows[i].hide()
                                if in_monitor
                                else self.mask_windows[i].show()
                            )
                    except Exception as e:
                        logging.error(f"处理显示器 {i} 时出错: {str(e)}")
                        continue  # 继续处理其他显示器

            if self.running:
                self.root.after(100, self.check_mouse_position)

        except Exception as e:
            logging.error(f"鼠标位置检测错误: {str(e)}")
            if self.running:
                # 如果发生错误，等待短暂时间后重试
                self.root.after(1000, self.check_mouse_position)

    def start_mouse_check(self):
        """启动鼠标位置检查"""
        self.check_mouse_position()

    def show_error_and_exit(self, error_message: str):
        """显示错误信息并退出程序"""
        logging.error(error_message)
        try:
            messagebox.showerror("错误", error_message)
        except:
            pass
        self.quit_app()

    def quit_app(self):
        """退出应用程序"""
        try:
            self.running = False
            with self._lock:
                for window in list(self.mask_windows.values()):
                    try:
                        window.destroy()
                    except:
                        pass
                self.mask_windows.clear()

            if hasattr(self, "tray_manager"):
                try:
                    self.tray_manager.stop()
                except:
                    pass

            if hasattr(self, "root") and self.root:
                try:
                    self.root.after(100, self.root.destroy)
                except:
                    pass

        except Exception as e:
            logging.error(f"退出程序时发生错误: {str(e)}")
            sys.exit(1)

    def run(self):
        """运行应用程序"""
        try:
            # 在新线程中运行托盘图标
            tray_thread = threading.Thread(target=self.tray_manager.run)
            tray_thread.daemon = True
            tray_thread.start()

            # 在主线程中运行主循环
            self.root.mainloop()

        except Exception as e:
            logging.error(f"程序运行错误: {str(e)}")
            self.show_error_and_exit(f"程序运行错误：{str(e)}")
