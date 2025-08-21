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
# 添加你自己的参数，并在 CONFIG 中修改 '显示常量'
# 将 '调试等级' 设为 3 可以查看机器人看到的内容并调整数值（会打开两个窗口）
# 或者，截取游戏截图并在画图等软件中查看像素坐标

# my_consts = DisplayConsts()


CONFIG = {
    # ---------- 每次运行 ----------
    '调试等级': 1,  # 数值越大信息越多，0 表示无输出；3 为交互式设置模式
    # 为 True 时，识别到方块颜色后会打印出来，便于设置 '方块颜色'
    # 但需要注意当前方块的颜色可能与下一帧不同
    '打印方块颜色': False,
    '按键延迟': 0.02,  # 如果出现误按可增大此值，想更快则减小
    'tetrio垃圾行': True,
    '第二块搜索宽度': 8,
    # 为 True 时，会多截一帧以确认方块位置
    # 会降低速度但提升稳定性
    '确认放置': True,
    '保守模式': False,  # 启用后 AI 更加保守
    '生存模式': False,  # True 时以“清理”模式开始
    '忽略延迟': False,  # True 时即使害怕也会硬降所有方块

    # ---------- 用户相关 ----------
    '显示常量': tetrio_default,
    '辅助窗口大小': '768x1536',
    '框选识别区域': True,  # 运行前手动框选棋盘与下一块区域

    # ---------- 游戏相关 ----------
    '游戏类型': 'tetr.io',
    '棋盘大小': [20, 10],
    '方块颜色': tetrio_colors,
    '额外行数': 2,  # 某些游戏（如 tetr.io）会在主区域上方生成方块

    # ---------- 其他 ----------
    '已警告': False,
}


def configure_fast():
    CONFIG['第二块搜索宽度'] = 8
    CONFIG['确认放置'] = False
    CONFIG['生存模式'] = True
    CONFIG['忽略延迟'] = True


# 调用以使用预设
configure_fast()

assert not (CONFIG['打印方块颜色'] and CONFIG['确认放置']), \
    '请禁用 "确认放置" 以避免与颜色输出混淆'
