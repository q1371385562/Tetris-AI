from typing import List

import numpy as np
import time
import keyboard

from config import CONFIG, name_piece

try:  # 兼容包内运行与直接运行
    from .find_landings import all_landings
    from .direct_keys import *
    from .figures import piece_weight, find_figure
    from .scan_field import get_field
    from .position import Position
except ImportError:  # 直接运行时回退到相对路径
    from find_landings import all_landings
    from direct_keys import *
    from figures import piece_weight, find_figure
    from scan_field import get_field
    from position import Position


class AI:
    def __init__(self):
        self.play_safe = CONFIG['保守模式']
        self.start_time = time.time()
        self.speed = 1
        self.clearing = CONFIG['生存模式']
        self.held_piece = -1
        self.scared = False
        self.choices_for_2nd = CONFIG['第二块搜索宽度']

    def hold_piece(self, piece_idx):
        click_key(hold)
        if CONFIG['调试等级'] >= 1:
            print(f'暂存 {name_piece(piece_idx)}，释放 {name_piece(self.held_piece)}')
        piece_idx, self.held_piece = self.held_piece, piece_idx
        return piece_idx

    @staticmethod
    def clear_line(field):
        """统计并清除满行"""
        full_cnt = 0
        i = 0
        while i < len(field):
            if np.sum(field[i]) == len(field[0]):
                full_cnt += 1
                field = np.delete(field, i, axis=0)
                field = np.insert(field, 0, np.zeros(len(field[0])), axis=0)
            else:
                i += 1
        return field, full_cnt

    @staticmethod
    def find_roofs(field: np.ndarray) -> (int, int, np.ndarray, int):
        """统计方块上方的空格数量和高度信息"""
        tops = np.zeros((10, 2))
        blank_cnt = 0
        blank_depth = 0
        for i in range(len(field)):
            for j in range(len(field[0])):
                if field[i][j]:
                    if tops[j][0] == 0:
                        tops[j][0] = 17 - i
                    tops[j][1] += 1
                elif tops[j][0] != 0:
                    blank_cnt += 1
                    blank_depth += tops[j][1] - 1
        return blank_cnt, int(np.max(tops[:, 0])), tops[:, 0], blank_depth

    @staticmethod
    def almost_full_line(field: np.ndarray) -> float:
        """对接近填满的行给予额外奖励"""
        score = 0.0
        line_width = len(field[0])
        for i in range(len(field)):
            ssum = np.sum(field[i])
            if ssum == line_width - 1:
                score += 2
            if ssum == line_width - 2:
                score += 0.5
        return score

    @staticmethod
    def find_hole(tops: np.ndarray) -> int:
        """统计左右两侧高度差超过 2 的“坑”数量"""
        cnt_hole = 0
        previous_height = 20
        tops[-1] = 20  # 最右边列暂不使用，视为很高
        for i in range(1, len(tops) - 1):
            if previous_height - 2 > tops[i] and tops[i] < tops[i + 1] - 2:
                cnt_hole += 1
            if previous_height - 4 > tops[i] and tops[i] < tops[i + 1] - 4:
                cnt_hole += min(tops[i - 1] - 4 - tops[i], tops[i + 1] - 4 - tops[i])
            previous_height = tops[i]
        return cnt_hole

    def update_state(self, field):
        blank_cnt, max_height, _, _ = self.find_roofs(field)
        if self.clearing and CONFIG['调试等级']:
            print('正在清理')
        if max_height >= 13 or self.speed == 3:
            self.scared = True
            if CONFIG['调试等级'] >= 1:
                print('害怕模式')
        else:
            self.scared = False

    def get_score(self, field: np.array, verbose=(CONFIG['调试等级'] >= 2)) -> (float, bool):
        """评估当前局面的好坏

        :param field: 当前棋盘
        :param verbose: 若为 True 则打印调试信息
        :return: 得分以及是否期待 TETRIS
        """
        expect_tetris = False
        score = 0
        # 计算当前局面的相关信息
        cleared_field, count_cleared = self.clear_line(field)
        blank_cnt, max_height, column_heights, blank_cumulative_depth = self.find_roofs(cleared_field)
        score += self.almost_full_line(cleared_field)
        # 清理 4 行（TETRIS）奖励极高
        if count_cleared >= 4:
            score += 1000
            expect_tetris = True

        score -= blank_cnt * 5
        score -= blank_cumulative_depth * 0.25

        # 尽可能清理场地
        if self.scared or self.clearing:
            score += 10 * count_cleared
            score -= max_height + max_height ** 1.4  # 最高方块的高度
            return score, expect_tetris

        score -= blank_cnt * 10  # 空格数
        score -= blank_cumulative_depth * 2

        # 当高度较低时高度影响较小
        if max_height > 7:
            score -= max_height ** 1.4
        score -= self.find_hole(column_heights) * 10
        if blank_cnt > 0:
            score += 5 * count_cleared
            return score, expect_tetris

        score -= 3 * count_cleared
        if column_heights[9] != 0:
            score -= 10  # 最右列应为空
            score -= column_heights[9]
        if verbose:
            print(cleared_field)
            print('消除行数', count_cleared)
            print(blank_cnt, max_height, column_heights, blank_cumulative_depth)
            print('坑洞', self.find_hole(column_heights))
            print('得分', score)
        return score, expect_tetris

    def calc_best(self, field: np.array, piece_idx: int) -> List[Position]:
        """计算方块所有可能落点并按得分排序"""
        results = all_landings(field, piece_idx)
        for i in range(len(results)):
            results[i].score, results[i].expect_tetris = self.get_score(results[i].field)
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def choose_action(self, field: np.array, piece_idx, can_hold) -> Position:
        """寻找当前局面下的最佳操作

        :param field: 当前棋盘
        :param piece_idx: 当前方块编号
        :param can_hold: 是否可以暂存方块（本回合已使用 hold 时为 False）
        :return: 最佳落点
        """
        # set inner flags for reward function
        self.update_state(field)

        # compute best placement for current piece
        result = self.calc_best(field, piece_idx)[0]
        if can_hold:
            # 考虑暂存的方块
            result_held = self.calc_best(field, self.held_piece)[0]
            if (result_held.score + piece_weight(self.held_piece)) > \
                    (result.score + piece_weight(piece_idx)):
                self.hold_piece(piece_idx)
                return result_held

        return result

    def choose_action_depth2(self, field: np.array, piece_idx: int, next_piece: int, can_hold: bool) -> Position:
        """在考虑下一块的情况下选择最佳操作

        :param field: 当前棋盘
        :param piece_idx: 当前方块编号
        :param next_piece: 下一块编号
        :param can_hold: 是否可以暂存
        :return: 最佳落点
        """
        if self.choices_for_2nd == 1:
            # 仅需计算当前方块
            return self.choose_action(field, piece_idx, can_hold)

        self.update_state(field)

        # 取得分最高的若干落点
        results = self.calc_best(field, piece_idx)[:self.choices_for_2nd]
        # 对每个落点，计算下一块的最佳落点
        for i in range(len(results)):
            # 清除满行
            results[i].field = self.clear_line(results[i].field)[0]
            # 计算下一块或暂存方块的得分
            sub_score = self.calc_best(results[i].field, next_piece)[0].score
            sub_score_hold = self.calc_best(results[i].field, self.held_piece)[0].score
            # 取较高分
            results[i].next_score = max(sub_score, sub_score_hold)
        # 对暂存方块进行相同处理
        if can_hold:
            results += self.calc_best(field, self.held_piece)[:self.choices_for_2nd]
            for i in range(self.choices_for_2nd, len(results)):
                results[i].field = self.clear_line(results[i].field)[0]
                sub_score = self.calc_best(results[i].field, next_piece)[0].score
                sub_score_hold = self.calc_best(results[i].field, piece_idx)[0].score
                results[i].next_score = max(sub_score, sub_score_hold)

        # 按总分选取最优，优先当前回合的 TETRIS
        optimal = max(results, key=lambda x: x.next_score + x.score + 1000 * x.expect_tetris)
        if optimal.piece == self.held_piece and self.held_piece != piece_idx:
            self.hold_piece(piece_idx)
        return optimal

    def place_piece(self, piece: int, rotation: int, x_pos: int, height: int, rot_now=0, x_pos_now=3, depth=0):
        """将方块移动到指定位置（下降前）并可选验证"""
        if depth == 3:
            if CONFIG['调试等级'] >= 1:
                print('放置方块递归深度达到 3')
            return
        rotate = (rotation - rot_now) % 4
        if rotate < 3:
            for i in range(rotate):
                click_key(rotate_k)
        else:
            click_key(rot_counterclock)
        move = x_pos - x_pos_now  # 3 is the starting position
        for i in range(abs(move)):
            if move > 0:
                click_key(mv_right)
            else:
                click_key(mv_left)

        # 验证方块是否放置在预期位置
        if CONFIG['确认放置']:
            time.sleep(0.09)
            field = get_field()[0]
            actual_pos = find_figure(field, piece, x_pos, max(0, 16 - height))
            if not actual_pos:
                if CONFIG['调试等级'] >= 1:
                    print('未找到方块')
            elif [rotation, x_pos] not in actual_pos:
                if CONFIG['调试等级'] >= 1:
                    print(f'发现误操作，实际位置 {actual_pos[0]}，应为 {rotation, x_pos}')
                self.place_piece(piece, rotation, x_pos, height,
                                 rot_now=actual_pos[0][0], x_pos_now=actual_pos[0][1], depth=depth+1)
            else:
                if CONFIG['调试等级'] >= 1:
                    print('位置正确')

    def place_piece_delay(self):
        if CONFIG['游戏类型'] == 'tetr.io':
            if (CONFIG['忽略延迟'] or not self.scared) and self.speed == 1:
                click_key(place_k)
                time.sleep(0.05)  # 稍等方块完全落下
            elif not self.scared and self.speed == 2:
                press_key(mv_down)
                time.sleep(0.3)
                release_key(mv_down)

        elif CONFIG['游戏类型'] == 'original':
            if time.time() - self.start_time < 160 and not self.scared and not self.play_safe:
                if time.time() - self.start_time < 120:
                    click_key(mv_down)
                click_key(mv_down)
                click_key(place_k)
                time.sleep(0.45)
            elif time.time() - self.start_time < 300:
                press_key(mv_down)
                time.sleep(max(0., 0.5 - (time.time() - self.start_time) / 1000))
                release_key(mv_down)
        else:
            click_key(place_k)

    def runtime_tuning(self):
        """运行时调节：

        速度模式：
        1 - 最慢级别，快速硬降
        2 - 中速，无硬降（可在 6 级开启）
        3 - 后期模式，总是害怕
        下一块计算路径数量：
        z, x, c - 1、4、8
        n - 尝试清理场地
        m - 关闭清理模式（尝试造 TETRIS）

        仅在新方块出现时检查按键，需要持续按住
        """
        if keyboard.is_pressed('1'):
            self.start_time = time.time()
            self.speed = 1
        elif keyboard.is_pressed('2'):
            self.start_time = time.time() - 160
            self.speed = 2
        elif keyboard.is_pressed('3'):
            self.start_time = time.time() - 300
            self.speed = 3

        if keyboard.is_pressed('z'):
            self.choices_for_2nd = 1
        elif keyboard.is_pressed('x'):
            self.choices_for_2nd = 4
        elif keyboard.is_pressed('c'):
            self.choices_for_2nd = 8

        if keyboard.is_pressed('n'):
            self.clearing = True
        elif keyboard.is_pressed('m'):
            self.clearing = False
