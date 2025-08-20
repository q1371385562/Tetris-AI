import numpy as np


class Position:
    """描述一次方块放置的结果"""

    def __init__(self, field: np.ndarray, rotation: int, x_pos: int, piece: int, score=0, expect_tetris=False):
        self.field = field
        self.rotation = rotation
        self.x_pos = x_pos
        self.piece = piece
        self.score = score
        self.expect_tetris = expect_tetris
        self.next_position = None
        self.next_score = 0

    def __call__(self):
        return self.field, self.rotation, self.x_pos, self.piece, self.score, self.expect_tetris
