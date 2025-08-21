import time
import winsound
import numpy as np

from config import CONFIG, name_piece

try:  # 兼容包内运行与直接运行两种方式
    from .scan_field import get_field
    from .display_interacive_setup import InteractiveSetup, ConstantsGUI, select_region
    from .figures import type_figure_ext
    from .AI_main import AI
    from .visualizer import Visualizer
except ImportError:
    from scan_field import get_field
    from display_interacive_setup import InteractiveSetup, ConstantsGUI, select_region
    from figures import type_figure_ext
    from AI_main import AI
    from visualizer import Visualizer


def main():
    can_hold_flag = True
    expected_rwd = 0
    ai = AI()
    position = None
    interactive_setup = None
    可视化 = Visualizer()
    if CONFIG.get('框选识别区域', False):
        CONFIG['显示常量'] = select_region(CONFIG['额外行数'])
    if CONFIG['调试等级'] >= 3:
        ConstantsGUI(CONFIG['显示常量'])
        interactive_setup = InteractiveSetup()

    # 预先调用以完成编译
    ai.calc_best(np.zeros((20, 10), dtype=int), 0)
    field, _ = get_field()
    可视化.update(field)
    print("编译完成")

    # 无限循环开始游戏
    while True:
        # 获取当前棋盘和下一块
        field, next_piece = get_field(interactive_setup)
        可视化.update(field)
        # 解析当前方块类型
        piece_idx = type_figure_ext(field[:5])
        if piece_idx is None:
            if not CONFIG['已警告']:
                print('\n未找到俄罗斯方块。\n'
                      '请确认在config.py中设置了DisplayConsts。\n')
                CONFIG['已警告'] = True
            continue
        if CONFIG['打印方块颜色']:
            print(f'刚刚打印颜色的方块编号：{piece_idx}')

        if CONFIG['调试等级'] >= 3:
            # 交互式设置模式下不进行游戏
            continue

        # 若暂存槽为空则先暂存
        if ai.held_piece == -1:
            ai.hold_piece(piece_idx)
            can_hold_flag = False
            continue

        # 为更好识别原版游戏的特殊处理
        if CONFIG['游戏类型'] == 'original':
            if position is not None and position.expect_tetris:
                # 假设不是误操作，TETRIS 动画遮挡界面因此不截图
                field = np.zeros((3, 10), dtype=np.int)
                field = np.concatenate((field, ai.clear_line(position.field)[0]))
                time.sleep(0.2)
            elif not ai.scared:
                field, next_piece = get_field()

        # 检查按键以调节运行时参数
        ai.runtime_tuning()

        # 检查得分是否与预期一致
        actual_score = ai.get_score(field[3:])[0]
        if CONFIG['调试等级'] >= 1:
            if expected_rwd != actual_score:
                winsound.Beep(2500, 500)
                print('\n操作偏差\n')
            if CONFIG['调试等级'] >= 2:
                print(field)
            print(f'当前得分 {actual_score}')

        # 未识别到下一块
        if next_piece == -1:
            if CONFIG['调试等级'] >= 1:
                print("未知的下一块")
            next_piece = 1  # 假设为方块作为中性选择

        calc_start_time = time.time()
        # 计算最佳落点
        position = ai.choose_action_depth2(field[3:], piece_idx, next_piece, can_hold_flag)

        if CONFIG['调试等级'] >= 1:
            # 打印调试信息
            print('计算耗时', time.time() - calc_start_time)
            print(f'为 {name_piece(position.piece)} 选择的落点：'
                  f'({position.rotation}, {position.x_pos})，得分 {position.score}')
            print(f'预计下一块 {name_piece(next_piece)} 可得分 {position.next_score}')
            if position.expect_tetris:
                print('期待 TETRIS')

        expected_rwd = ai.get_score(ai.clear_line(position.field)[0])[0]
        # 模拟按键放置方块
        ai.place_piece(position.piece, position.rotation, position.x_pos, ai.find_roofs(position.field)[1])
        # 等待方块落定
        ai.place_piece_delay()

        can_hold_flag = True
        if CONFIG['调试等级'] >= 1:
            print()


if __name__ == '__main__':
    time.sleep(1)
    main()
