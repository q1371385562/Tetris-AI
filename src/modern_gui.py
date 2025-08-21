import io
from dataclasses import dataclass

import numpy as np
import PySimpleGUI as sg
from mss import mss
from PIL import Image

from config import CONFIG
from src.display_consts import DisplayConsts


def _np_to_bytes(img: np.ndarray) -> bytes:
    """将 numpy 图像转为 PNG 字节"""
    with io.BytesIO() as output:
        Image.fromarray(img).save(output, format="PNG")
        return output.getvalue()


@dataclass
class Region:
    start: tuple
    end: tuple


class BoardGUI:
    """使用 PySimpleGUI 显示棋盘的简单窗口"""

    def __init__(self):
        sg.theme("DarkBlue3")
        self.cell = 24
        width, height = 10 * self.cell, 20 * self.cell
        layout = [[sg.Graph((width, height), (0, height), (width, 0), key="-G-")]]
        self.window = sg.Window("棋盘", layout, finalize=True)
        self.graph = self.window["-G-"]

    def update(self, field: np.ndarray):
        self.graph.erase()
        for y in range(field.shape[0]):
            for x in range(field.shape[1]):
                if field[y, x]:
                    x0, y0 = x * self.cell, y * self.cell
                    self.graph.draw_rectangle(
                        (x0, y0), (x0 + self.cell, y0 + self.cell), fill_color="green", line_color="gray"
                    )
        self.window.refresh()

    def close(self):
        self.window.close()


def _select_once(img: np.ndarray, title: str) -> Region:
    """在截图上拖动鼠标选择矩形区域"""
    h, w, _ = img.shape
    graph = sg.Graph((w, h), (0, h), (w, 0), key="-GRAPH-", change_submits=True, drag_submits=True)
    layout = [[sg.Text(title)], [graph], [sg.Button("确定")]]
    win = sg.Window("选择区域", layout, finalize=True)
    graph.draw_image(data=_np_to_bytes(img), location=(0, 0))
    start = end = None
    rect = None
    while True:
        event, values = win.read()
        if event in (sg.WIN_CLOSED, "确定") and start and end:
            break
        if event == "-GRAPH-":
            x, y = values["-GRAPH-"]
            if start is None:
                start = (x, y)
            else:
                end = (x, y)
                if rect:
                    graph.delete_figure(rect)
                rect = graph.draw_rectangle(start, end, line_color="red")
    win.close()
    return Region(start, end)


def select_region() -> DisplayConsts:
    """手动选择棋盘与下一块区域"""
    with mss() as sct:
        screenshot = np.array(sct.grab(sct.monitors[1]))
    board = _select_once(screenshot, "拖动选择棋盘区域后点击确定")
    nxt = _select_once(screenshot, "拖动选择下一块区域后点击确定")

    def _norm(r: Region):
        (x1, y1), (x2, y2) = r.start, r.end
        left, right = sorted([x1, x2])
        top, bottom = sorted([y1, y2])
        return top, bottom, left, right

    top, bottom, left, right = _norm(board)
    ntop, nbottom, nleft, nright = _norm(nxt)
    consts = DisplayConsts(top, bottom, left, right, ntop, nbottom, nleft, nright, CONFIG['额外行数'])
    print("新的显示常量:", consts)
    return consts
