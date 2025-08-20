import numpy as np
from src.display_consts import DisplayConsts


# 方块的编号对应如下：
# 0 - 长条，1 - 方块，2 - T，3 - L，4 - 反L，5 - S，6 - Z
PIECE_NAMES = ['长条', '方块', 'T', 'L', '反L', 'S', 'Z']


def name_piece(piece: int) -> str:
    return PIECE_NAMES[piece]


# 原版游戏中的 RGB 颜色
original_colors = np.zeros((7, 3), int)
original_colors[0] = (180, 228, 230)
original_colors[1] = (247, 228, 182)
original_colors[2] = (140, 99, 177)
original_colors[3] = (148, 177, 228)
original_colors[4] = (235, 180, 128)
original_colors[5] = (235, 161, 180)
original_colors[6] = (177, 240, 171)

# tetr.io 版本的 RGB 颜色
tetrio_colors = np.zeros((7, 3), int)
tetrio_colors[0] = (50, 179, 131)
tetrio_colors[1] = (179, 153, 49)
tetrio_colors[2] = (165, 63, 155)
tetrio_colors[3] = (80, 63, 166)
tetrio_colors[4] = (179, 99, 50)
tetrio_colors[5] = (181, 53, 60)
tetrio_colors[6] = (133, 181, 52)

# 屏幕识别所需的关键像素位置
tetrio_default = DisplayConsts(top=465, bottom=1780, left=1590, right=2250,
                               next_top=600, next_bottom=635, next_left=2405, next_right=2535, num_extra_rows=2)


# -------------------------------- 需要手动设置 --------------------------------
# 添加你自己的参数，并在 CONFIG 中修改 'display consts'
# 将 'debug status' 设为 3 可以查看机器人看到的内容并调整数值（会打开两个窗口）
# 或者，截取游戏截图并在画图等软件中查看像素坐标

# my_consts = DisplayConsts()


CONFIG = {
    # ---------- 每次运行 ----------
    'debug status': 1,  # 数值越大信息越多，0 表示无输出；3 为交互式设置模式
    # 为 True 时，识别到方块颜色后会打印出来，便于设置 'piece colors'
    # 但需要注意当前方块的颜色可能与下一帧不同
    'print piece color': False,
    'key press delay': 0.02,  # 如果出现误按可增大此值，想更快则减小
    'tetrio garbage': True,
    'starting choices for 2nd': 8,
    # 为 True 时，会多截一帧以确认方块位置
    # 会降低速度但提升稳定性
    'confirm placement': True,
    'play safe': False,  # 启用后 AI 更加保守
    'play for survival': False,  # True 时以“清理”模式开始
    'override delay': False,  # True 时即使害怕也会硬降所有方块

    # ---------- 用户相关 ----------
    'display consts': tetrio_default,
    'helper window size': '768x1536',

    # ---------- 游戏相关 ----------
    'game': 'tetr.io',
    'playing field size': [20, 10],
    'piece colors': tetrio_colors,
    'extra rows': 2,  # 某些游戏（如 tetr.io）会在主区域上方生成方块

    # ---------- 其他 ----------
    'gave warning': False,
}


def configure_fast():
    CONFIG['starting choices for 2nd'] = 8
    CONFIG['confirm placement'] = False
    CONFIG['play for survival'] = True
    CONFIG['override delay'] = True


# 调用以使用预设
configure_fast()

assert not (CONFIG['print piece color'] and CONFIG['confirm placement']), \
    '请禁用 "confirm placement" 以避免与颜色输出混淆'
