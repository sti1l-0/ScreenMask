from PIL import Image, ImageDraw
import os


def create_monitor_icon(size=64, save_path="icons"):
    """创建显示器样式的图标并保存"""
    # 创建保存目录
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 创建不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    icons = []

    for icon_size in sizes:
        # 创建透明背景的图像
        image = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # 计算尺寸
        padding = icon_size // 8
        screen_width = icon_size - (padding * 2)
        screen_height = (screen_width * 9) // 16
        stand_width = screen_width // 3
        stand_height = icon_size // 6

        # 显示器位置
        screen_top = padding
        screen_left = padding

        # 绘制显示器边框（深灰色）
        border_width = max(1, icon_size // 32)
        draw.rectangle(
            [
                screen_left - border_width,
                screen_top - border_width,
                screen_left + screen_width + border_width,
                screen_top + screen_height + border_width,
            ],
            fill=(64, 64, 64),
        )

        # 绘制屏幕（稍浅的灰色）
        draw.rectangle(
            [
                screen_left,
                screen_top,
                screen_left + screen_width,
                screen_top + screen_height,
            ],
            fill=(96, 96, 96),
        )

        # 添加屏幕高光效果
        highlight_width = max(1, screen_width // 8)
        draw.rectangle(
            [
                screen_left + highlight_width,
                screen_top + highlight_width,
                screen_left + screen_width - highlight_width,
                screen_top + screen_height - highlight_width,
            ],
            fill=(128, 128, 128),
        )

        # 计算支架位置
        stand_top = screen_top + screen_height
        stand_left = screen_left + (screen_width - stand_width) // 2

        # 绘制支架
        draw.rectangle(
            [
                stand_left + stand_width // 3,
                stand_top,
                stand_left + stand_width * 2 // 3,
                stand_top + stand_height // 2,
            ],
            fill=(200, 200, 200),
        )

        # 绘制底座
        draw.rectangle(
            [
                stand_left,
                stand_top + stand_height - stand_height // 2,
                stand_left + stand_width,
                stand_top + stand_height,
            ],
            fill=(180, 180, 180),
        )

        icons.append(image)

    # 保存为ICO文件
    icons[0].save(
        os.path.join(save_path, "monitor.ico"),
        format="ICO",
        sizes=[(size, size) for size in sizes],
        append_images=icons[1:],
    )

    # 保存为PNG文件（使用最大尺寸）
    icons[-1].save(os.path.join(save_path, "monitor.png"), format="PNG")

    print(f"图标已保存到 {save_path} 目录")


if __name__ == "__main__":
    create_monitor_icon()
