import PyInstaller.__main__
import os
import sys

# 确保图标文件存在
if not os.path.exists("icons/monitor.ico"):
    print("错误: 找不到图标文件 'icons/monitor.ico'")
    sys.exit(1)

# PyInstaller 配置
PyInstaller.__main__.run(
    [
        "run.py",  # 主程序文件
        "--name=ScreenMask",  # 生成的 exe 名称
        "--windowed",  # 使用 Windows 子系统（不显示控制台窗口）
        "--icon=icons/monitor.ico",  # 程序图标
        "--add-data=icons/monitor.ico;icons/",  # 添加图标资源文件
        "--add-data=icons/monitor.png;icons/",  # 添加图标资源文件
        "--noconfirm",  # 覆盖现有文件夹
        "--clean",  # 清理临时文件
        "--onefile",  # 打包成单个文件
    ]
)
