import win32api
from screeninfo import Monitor
from typing import Dict, Tuple


class MouseTracker:
    @staticmethod
    def get_mouse_position() -> Tuple[int, int]:
        """获取鼠标位置"""
        return win32api.GetCursorPos()

    @staticmethod
    def is_mouse_in_monitor(mouse_pos: Tuple[int, int], monitor: Monitor) -> bool:
        """检查鼠标是否在指定显示器内"""
        mouse_x, mouse_y = mouse_pos
        return (
            monitor.x <= mouse_x < monitor.x + monitor.width
            and monitor.y <= mouse_y < monitor.y + monitor.height
        )
