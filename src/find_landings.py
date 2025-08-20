from copy import deepcopy
from typing import List

import numpy as np

from position import Position
from figures import array_of_figures as pieces


def check_collision(field, piece, piece_pos, piece_idx):
    r = 4
    if piece_idx != 0:
        # 只有长条方块会占满 4x4 网格，其余方块只需检查 3x3
        r -= 1
    for i in range(r):
        for j in range(r):
            if piece[i][j]:
                if (i + piece_pos[0] >= len(field)) or (j + piece_pos[1] >= len(field[0])) or (i + piece_pos[0] < 0) or \
                        (j + piece_pos[1] < 0) or field[i + piece_pos[0]][j + piece_pos[1]]:
                    return True
    return False


def land(field: np.ndarray, piece: np.ndarray, x_pos: int, piece_idx: int) -> np.ndarray:
    """模拟方块从指定位置下落至棋盘"""
    pos_now = [0, x_pos]
    while not check_collision(field, piece, pos_now, piece_idx):
        pos_now[0] += 1
    if pos_now[0] == 0:
        return None
    pos_now[0] -= 1
    for i in range(4):
        for j in range(4):
            if i + pos_now[0] < len(field) and j + pos_now[1] < len(field[0]):
                field[i + pos_now[0]][j + pos_now[1]] += piece[i][j]
    return field


def all_landings(field: np.array, piece_index: int) -> List[Position]:
    """
    calculates all possible results
    :param field:
    :param piece_index:
    :return: Position
    """
    results = []
    for rotation in range(len(pieces[piece_index])):
        for x_pos in range(-3, 10):
            res = land(deepcopy(field), pieces[piece_index][rotation], x_pos, piece_index)
            if res is not None:
                results.append(Position(res, rotation, x_pos, piece_index))
    return results
