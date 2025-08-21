import time
import winsound
import numpy as np

from config import CONFIG, name_piece

try:
    from .scan_field import get_field
    from .figures import type_figure_ext
    from .AI_main import AI
except ImportError:
    from scan_field import get_field
    from figures import type_figure_ext
    from AI_main import AI

try:
    from .modern_gui import select_region, BoardGUI
except ImportError as e:
    raise ImportError(
        "缺少 PySimpleGUI 依赖，请先执行 `pip install -r requirements.txt` 后再运行。"
    ) from e


def main():
    ai = AI()
    can_hold_flag = True
    expected_rwd = 0
    display_consts = select_region() if CONFIG.get('框选识别区域', True) else CONFIG['显示常量']
    gui = BoardGUI()

    ai.calc_best(np.zeros((20, 10), dtype=int), 0)
    print("编译完成")

    warned = False
    position = None
    while True:
        field, next_piece = get_field(display_consts)
        gui.update(field)
        piece_idx = type_figure_ext(field[:5])
        if piece_idx is None:
            if not warned:
                print('未找到俄罗斯方块。请重新选择区域。')
                warned = True
            continue

        if ai.held_piece == -1:
            ai.hold_piece(piece_idx)
            can_hold_flag = False
            continue

        ai.runtime_tuning()

        actual_score = ai.get_score(field[3:])[0]
        if CONFIG['调试等级'] >= 1:
            if expected_rwd != actual_score:
                winsound.Beep(2500, 500)
                print('\n操作偏差\n')
            print(f'当前得分 {actual_score}')

        if next_piece == -1:
            if CONFIG['调试等级'] >= 1:
                print('未知的下一块')
            next_piece = 1

        calc_start_time = time.time()
        position = ai.choose_action_depth2(field[3:], piece_idx, next_piece, can_hold_flag)

        if CONFIG['调试等级'] >= 1:
            print('计算耗时', time.time() - calc_start_time)
            print(f'为 {name_piece(position.piece)} 选择的落点：'
                  f'({position.rotation}, {position.x_pos})，得分 {position.score}')
            print(f'预计下一块 {name_piece(next_piece)} 可得分 {position.next_score}')
            if position.expect_tetris:
                print('期待 TETRIS')
            print()

        expected_rwd = ai.get_score(ai.clear_line(position.field)[0])[0]
        ai.place_piece(position.piece, position.rotation, position.x_pos, ai.find_roofs(position.field)[1])
        ai.place_piece_delay()
        can_hold_flag = True


if __name__ == '__main__':
    time.sleep(1)
    main()
