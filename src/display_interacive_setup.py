import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading

# 设定中文字体，避免图像与界面文字乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'DengXian']
plt.rcParams['axes.unicode_minus'] = False

from config import CONFIG


class InteractiveSetup:
    def __init__(self):
        import matplotlib
        matplotlib.use('TkAgg')
        plt.ion()
        self.fig, self.axes = plt.subplots(1, 3, figsize=(7, 5))
        self.axes[0].set_title("原始棋盘")
        self.axes[1].set_title("处理后棋盘")
        self.axes[2].set_title("下一块")
        for ax in self.axes:
            ax.axis('off')
        self.buffers = [self.axes[0].imshow(np.zeros((20, 10, 3))),
                        self.axes[1].imshow(np.zeros((20, 10, 3))),
                        self.axes[2].imshow(np.zeros((5, 5, 3)))]

    def render_frame(self, field, simplified, next_img, next_piece):
        self.buffers[0].set_array(field.copy()[:, :, 2::-1])  # BGRA 转为 RGB
        img_simplified = simplified.copy()
        # 转为三通道后显示效果更好
        img_simplified = np.expand_dims(img_simplified, axis=2)
        img_simplified = np.broadcast_to(img_simplified, (img_simplified.shape[0], img_simplified.shape[1], 3))
        self.buffers[1].set_array(img_simplified*255)
        self.buffers[2].set_array(next_img.copy()[:, :, 2::-1])
        self.axes[2].set_title(f"下一块（识别为 {next_piece}）")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class ConstantsGUI:
    def __init__(self, display_consts):
        self.display_consts = display_consts
        self.root = None
        self.vars = None
        self.font = ('SimHei', 14)
        self.thread = threading.Thread(target=self.create_gui, daemon=True)
        self.thread.start()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("显示常量设置")
        self.root.geometry(CONFIG['辅助窗口大小'])

        style = ttk.Style()
        style.configure('Large.TLabel', font=self.font)
        style.configure('Large.TEntry', font=self.font)
        style.configure('Large.TButton', font=self.font)

        self.vars = {
            'top': tk.IntVar(value=self.display_consts.top),
            'bottom': tk.IntVar(value=self.display_consts.bottom),
            'left': tk.IntVar(value=self.display_consts.left),
            'right': tk.IntVar(value=self.display_consts.right),
            'next_top': tk.IntVar(value=self.display_consts.next_top),
            'next_bottom': tk.IntVar(value=self.display_consts.next_bottom),
            'next_left': tk.IntVar(value=self.display_consts.next_left),
            'next_right': tk.IntVar(value=self.display_consts.next_right),
            'num_extra_rows': tk.IntVar(value=self.display_consts.num_extra_rows)
        }

        labels = {
            'top': '顶部',
            'bottom': '底部',
            'left': '左侧',
            'right': '右侧',
            'next_top': '下一块顶部',
            'next_bottom': '下一块底部',
            'next_left': '下一块左侧',
            'next_right': '下一块右侧',
            'num_extra_rows': '额外行数'
        }

        for name, var in self.vars.items():
            frame = ttk.Frame(self.root)
            frame.pack(fill='x', padx=10, pady=5)

            ttk.Label(frame, text=f"{labels[name]}:", style='Large.TLabel').pack(side='left')

            # 创建按钮框架
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(side='right')

            # 上下调节按钮
            up_btn = ttk.Button(btn_frame, text="▲", width=3,
                                command=lambda v=var: self.adjust_value(v, 5))
            up_btn.pack(side='top')

            down_btn = ttk.Button(btn_frame, text="▼", width=3,
                                  command=lambda v=var: self.adjust_value(v, -5))
            down_btn.pack(side='bottom')

            # 输入框
            entry = ttk.Entry(frame, textvariable=var, font=self.font, width=10)
            entry.pack(side='right', padx=5)

        ttk.Button(self.root, text="全部更新", command=self.update_all,
                  style='Large.TButton').pack(pady=20)

        ttk.Label(self.root, text="每次更新都会在控制台打印新的显示常量，\n记得复制到 config.py 中",
                  style='Large.TLabel').pack(pady=20)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def update_value(self, name):
        value = self.vars[name].get()
        setattr(self.display_consts, name, value)

    def adjust_value(self, var, delta):
        current = var.get()
        var.set(current + delta)
        self.update_all()

    def update_all(self):
        for name in self.vars:
            self.update_value(name)
        self.display_consts.update()
        print("显示常量已更新:", self.display_consts)

    def on_closing(self):
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None

    def is_alive(self):
        return self.thread.is_alive()

