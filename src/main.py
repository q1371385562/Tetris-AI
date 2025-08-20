import time

import winsound

from config import CONFIG, name_piece
from src.scan_field import get_field
from src.display_interacive_setup import InteractiveSetup, ConstantsGUI
from src.figures import type_figure_ext
from src.AI_main import AI
from src.visualizer import Visualizer
import numpy as np


def main():
    can_hold_flag = True
    expected_rwd = 0
    ai = AI()
    position = None
    interactive_setup = None
    可视化 = Visualizer()
    if CONFIG['debug status'] >= 3:
        ConstantsGUI(CONFIG['display consts'])
        interactive_setup = InteractiveSetup()

    # call jit-compiling functions to compile them
    ai.calc_best(np.zeros((20, 10), dtype=int), 0)
    field, _ = get_field()
    可视化.update(field)
    print("编译完成")

    # infinite playing cycle
    while True:
        # get playing grid and the next piece
        field, next_piece = get_field(interactive_setup)
        可视化.update(field)
        # parse current tetris piece
        piece_idx = type_figure_ext(field[:5])
        if piece_idx is None:
            if not CONFIG['gave warning']:
                print('\n未找到俄罗斯方块。\n'
                      '请确认在config.py中设置了DisplayConsts。\n')
                CONFIG['gave warning'] = True
            continue
        if CONFIG['print piece color']:
            print(f'刚刚打印颜色的方块编号：{piece_idx}')

        if CONFIG['debug status'] >= 3:
            # in the interactive setup, do not play the game
            continue

        # hold if nothing is held
        if ai.held_piece == -1:
            ai.hold_piece(piece_idx)
            can_hold_flag = False
            continue

        # shenanigans for better parsing of the original game
        if CONFIG['game'] == 'original':
            if position is not None and position.expect_tetris:
                # hoping that it was not a misclick, not taking a screenshot because TETRIS blocks the view
                field = np.zeros((3, 10), dtype=np.int)
                field = np.concatenate((field, ai.clear_line(position.field)[0]))
                time.sleep(0.2)
            elif not ai.scared:
                field, next_piece = get_field()

        # check held keys for runtime AI tuning
        ai.runtime_tuning()

        # check if the result is expected
        actual_score = ai.get_score(field[3:])[0]
        if CONFIG['debug status'] >= 1:
            if expected_rwd != actual_score:
                winsound.Beep(2500, 500)
                print('\n操作偏差\n')
            if CONFIG['debug status'] >= 2:
                print(field)
            print(f'当前得分 {actual_score}')

        # next piece is not recognized
        if next_piece == -1:
            if CONFIG['debug status'] >= 1:
                print("未知的下一块")
            next_piece = 1  # assume square as it is the most neutral one

        calc_start_time = time.time()
        # 计算最佳落点
        position = ai.choose_action_depth2(field[3:], piece_idx, next_piece, can_hold_flag)

        if CONFIG['debug status'] >= 1:
            # 打印调试信息
            print('计算耗时', time.time() - calc_start_time)
            print(f'为 {name_piece(position.piece)} 选择的落点：'
                  f'({position.rotation}, {position.x_pos})，得分 {position.score}')
            print(f'预计下一块 {name_piece(next_piece)} 可得分 {position.next_score}')
            if position.expect_tetris:
                print('期待 TETRIS')

        expected_rwd = ai.get_score(ai.clear_line(position.field)[0])[0]
        # emulate key presses to place the piece
        ai.place_piece(position.piece, position.rotation, position.x_pos, ai.find_roofs(position.field)[1])
        # wait for everything to settle down
        ai.place_piece_delay()

        can_hold_flag = True
        if CONFIG['debug status'] >= 1:
            print()


if __name__ == '__main__':
    time.sleep(1)
    main()
