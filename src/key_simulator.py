import keyboard

def press(key: str) -> None:
    """模拟按键，当前主程序未调用"""
    keyboard.press(key)
    keyboard.release(key)
