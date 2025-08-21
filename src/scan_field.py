import numpy as np
from mss import mss

from config import CONFIG
from src.display_consts import DisplayConsts

screen_capture = mss()
piece_colors = CONFIG['方块颜色']


def simplified(pixels: np.ndarray) -> np.ndarray:
    """将截图转为仅含方块与空格的二维数组"""
    dark_boundary = [130, 100, 90]
    if CONFIG['tetrio垃圾行']:
        dark_boundary = [70, 60, 60]
    field0 = (pixels[:, :, 0] < dark_boundary[0]).astype(int)
    field1 = (pixels[:, :, 1] < dark_boundary[1]).astype(int)
    field2 = (pixels[:, :, 2] < dark_boundary[2]).astype(int)
    dark_pixels = field0 * field1 * field2

    field_white0 = (pixels[:, :, 0] > 200).astype(int)
    field_white1 = (pixels[:, :, 1] > 200).astype(int)
    field_white2 = (pixels[:, :, 2] > 200).astype(int)
    white_pixels = field_white0 * field_white1 * field_white2

    excluded_pixels = dark_pixels + white_pixels
    field = 1 - excluded_pixels
    return field


def get_figure_by_color(screen: np.ndarray) -> int:
    """通过像素颜色识别下一块类型"""
    pixels = screen[:, :, :3].reshape(-1, 3).astype(int)
    colors = piece_colors[:, ::-1].astype(int)
    diff = np.abs(pixels[None, :, :] - colors[:, None, :]).sum(axis=2)
    min_dist = diff.min(axis=1)
    if np.min(min_dist) < 30:
        return int(np.argmin(min_dist))
    return -1


def get_field(display_consts: DisplayConsts) -> (np.ndarray, int):
    """截取屏幕并计算棋盘状态"""
    img = np.array(screen_capture.grab(display_consts.get_screen_bounds()))
    field_img = display_consts.get_field_from_screen(img)
    pixels = simplified(field_img)
    next_img = display_consts.get_next(img)
    next_piece = get_figure_by_color(next_img)

    field = np.zeros((20 + CONFIG['额外行数'], 10))
    cell_size = pixels.shape[1] // 10
    vertical_centers = np.array(
        np.linspace(cell_size // 2, pixels.shape[0] + cell_size // 2, 21 + CONFIG['额外行数'])[:-1], int
    )
    if vertical_centers[-1] > pixels.shape[0]:
        print("宽高比例非 1:2，单元格大小可能不正确")
        return field, next_piece
    horizontal_centers = np.array(np.linspace(cell_size // 2, pixels.shape[1] + cell_size // 2, 11)[:-1], int)

    offsets_to_check = []
    steps = [-cell_size // 3, 0, cell_size // 3]
    nearby = np.zeros((len(steps) ** 2))
    for v_offset in steps:
        for h_offset in steps:
            offsets_to_check.append((v_offset, h_offset))
    for i, v in enumerate(vertical_centers):
        for j, h in enumerate(horizontal_centers):
            for k, (v_offset, h_offset) in enumerate(offsets_to_check):
                nearby[k] = pixels[v + v_offset][h + h_offset]
            if np.mean(nearby) > 0.75:
                field[i][j] = 1
                if CONFIG['打印方块颜色'] and i < 3:
                    piece_bgr = field_img[v][h][:3].astype(int)
                    print(f'新方块的 RGB 颜色: ({piece_bgr[2]}, {piece_bgr[1]}, {piece_bgr[0]})')
    return field, next_piece
