from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from mss import mss

from config import CONFIG
from src.display_interacive_setup import InteractiveSetup

screen_capture = mss()
piece_colors = CONFIG['方块颜色']


def simplified(pixels: np.array) -> np.array:
    """将截图转为仅含方块与空格的二维数组

    :param pixels: 屏幕 BGR 像素
    :return: 仅包含 0/1 的棋盘数组
    """
    dark_boundary = [130, 100, 90]
    if CONFIG['tetrio垃圾行']:
        # 对垃圾行放宽暗色阈值
        dark_boundary = [70, 60, 60]
    field0 = np.array(pixels[:, :, 0] < dark_boundary[0], int)  # 蓝色通道
    field1 = np.array(pixels[:, :, 1] < dark_boundary[1], int)  # 绿色通道
    field2 = np.array(pixels[:, :, 2] < dark_boundary[2], int)  # 红色通道
    # 三个通道都很暗的像素必定不是方块
    dark_pixels = field0 * field1 * field2

    field_white0 = np.array(pixels[:, :, 0] > 200, int)
    field_white1 = np.array(pixels[:, :, 1] > 200, int)
    field_white2 = np.array(pixels[:, :, 2] > 200, int)
    # 三个通道都很亮的像素也不是方块
    white_pixels = field_white0 * field_white1 * field_white2

    # 结合暗像素和亮像素，得到所有非方块像素
    excluded_pixels = dark_pixels + white_pixels
    # 方块处为 1，空格为 0
    field = 1 - excluded_pixels
    return field


def cmp_pixel(pixels, color):
    """计算像素与颜色的曼哈顿距离"""
    return np.abs(pixels[:, 0] - color[2]) + \
           np.abs(pixels[:, 1] - color[1]) + \
           np.abs(pixels[:, 2] - color[0])


def get_figure_by_color(screen: np.array):
    pixels = screen[:, :, :3].reshape(-1, 3).astype(int)
    distances = np.zeros((len(piece_colors), len(pixels)), dtype=int)

    for i in range(len(piece_colors)):
        distances[i] = cmp_pixel(pixels, piece_colors[i])

    min_distances = np.min(distances, axis=1)  # 形状为 (len(piece_colors),)
    if np.min(min_distances) < 30:
        return np.argmin(min_distances)
    return -1


def get_field(interactive_setup: Optional[InteractiveSetup] = None) -> (np.array, int):
    """截取屏幕并计算棋盘状态

    :return: 棋盘矩阵及下一块编号
    """
    img = np.array(screen_capture.grab(CONFIG['显示常量'].get_screen_bounds()))
    field_img = CONFIG['显示常量'].get_field_from_screen(img)
    pixels = simplified(field_img)
    next_img = CONFIG['显示常量'].get_next(img)
    next_piece = get_figure_by_color(next_img)

    if interactive_setup is not None:
        interactive_setup.render_frame(field_img, pixels, next_img, next_piece)

    # 初始化为空棋盘
    field = np.zeros((20 + CONFIG['额外行数'], 10))
    # 计算网格中心点
    cell_size = pixels.shape[1] // 10
    vertical_centers = np.array(np.linspace(cell_size // 2, pixels.shape[0] + cell_size // 2, 21 + CONFIG['额外行数'])[:-1], int)
    if vertical_centers[-1] > pixels.shape[0]:
        print("宽高比例非 1:2，单元格大小可能不正确")
        return field, next_piece
    horizontal_centers = np.array(np.linspace(cell_size // 2, pixels.shape[1] + cell_size // 2, 11)[:-1], int)

    offsets_to_check = []
    steps = [-cell_size//3, 0, cell_size//3]
    nearby = np.zeros((len(steps)**2))
    for v_offset in steps:
        for h_offset in steps:
            offsets_to_check.append((v_offset, h_offset))
    # 遍历所有单元格中心
    for i, v in enumerate(vertical_centers):
        for j, h in enumerate(horizontal_centers):
            for k, (v_offset, h_offset) in enumerate(offsets_to_check):
                nearby[k] = pixels[v + v_offset][h + h_offset]
            if np.mean(nearby) > 0.75:
                field[i][j] = 1
                if CONFIG['打印方块颜色'] and i < 3:
                    piece_bgr = field_img[v][h][:3].astype(dtype=int)
                    print(f'新方块的 RGB 颜色: '
                          f'({piece_bgr[2]}, {piece_bgr[1]}, {piece_bgr[0]})')
    return field, next_piece
