import matplotlib.pyplot as plt
import numpy as np

# 设定中文字体，避免窗口中文字出现乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'DengXian']
plt.rcParams['axes.unicode_minus'] = False

class Visualizer:
    """简单的俄罗斯方块棋盘可视化窗口"""

    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("俄罗斯方块AI可视化")
        self.im = self.ax.imshow(np.zeros((20, 10)), cmap="tab20", vmin=0, vmax=7)
        self.ax.axis('off')
        self.fig.show()

    def update(self, field):
        """更新当前棋盘显示"""
        self.im.set_data(field)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.001)
