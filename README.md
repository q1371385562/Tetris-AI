# 俄罗斯方块 AI

我们构建了一个能在在线俄罗斯方块中比我们更强的机器人，它甚至还赢过几美元。

该机器人通过截图读取棋盘并模拟按键，因此可以适配任意俄罗斯方块游戏。

读取到棋盘后，它会使用算法计算最佳落点并执行。

算法提供多种模式，例如追求 “TETRIS”（一次消除四行）的策略。

### 演示
模式 1 的游戏画面

![demo mode 1](https://media.giphy.com/media/kg1Ng8ZXTUQ2efOpUk/giphy.gif)

模式 2 在另一款游戏中的表现

![demo mode 2](https://user-images.githubusercontent.com/27450370/147476623-7acc036e-7195-409b-a2ec-d24e489aadf2.gif)

## 使用说明

### 运行方法
运行前请先安装依赖：

```bash
pip install -r requirements.txt
```

1. 截取一张你所玩俄罗斯方块的游戏界面
2. 在 `config.py` 中创建一个 `DisplayConsts` 实例
3. 将 `CONFIG` 中的 `display consts` 设置为你的实例
4. 如有需要，定义 `colors` 数组以识别下一块的颜色
5. 调整其他配置参数
6. 在项目根目录运行 `python src/main.py`，或使用模块方式 `python -m src.main`
7. 切换到游戏窗口

### 运行时调节
游戏过程中可以通过按键控制机器人行为（仅在新方块出现时检查，需要按住）：

    下落速度
    1 - 最快，总是硬降
    2 - 取消硬降
    3 - 自由下落，机器人会“害怕”
    下一块的计算路径数量：
    z, x, c - 1、4、8
    n - 尝试清理场地
    m - 关闭清理模式（专注于造 TETRIS）
