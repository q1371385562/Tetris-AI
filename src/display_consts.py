class DisplayConsts:
    """保存关键像素位置以截取屏幕。

    每位用户都需要单独设置。
    """
    def __init__(self, top, bottom, left, right, next_top, next_bottom, next_left, next_right, num_extra_rows=0):
        # 游戏区域的四个边界（仅 20x10 的主区域）
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

        # 下一块所在的小区域，无需包含整块
        self.next_top = next_top
        self.next_bottom = next_bottom
        self.next_left = next_left
        self.next_right = next_right

        self.num_extra_rows = num_extra_rows

        self.update()

    def update(self):
        row_height = (self.bottom - self.top) // 20
        self.extra_rows = self.top - self.num_extra_rows * row_height
        self.vertical_offset = min(self.extra_rows, self.next_top)
        self.horizontal_offset = min(self.left, self.next_left)

    def get_field_from_screen(self, img):
        return img[self.extra_rows-self.vertical_offset:self.bottom-self.vertical_offset,
                   self.left-self.horizontal_offset:self.right-self.horizontal_offset]

    def get_next(self, img):
        return img[self.next_top-self.vertical_offset:self.next_bottom-self.vertical_offset,
                   self.next_left-self.horizontal_offset:self.next_right-self.horizontal_offset]

    def get_screen_bounds(self):
        """返回需要截取的屏幕区域"""
        bottom = max(self.bottom, self.next_bottom)
        right = max(self.right, self.next_right)
        return {
            "left": self.horizontal_offset,
            "width": right - self.horizontal_offset,
            "top": self.vertical_offset,
            "height": bottom - self.vertical_offset
        }

    def __str__(self):
        return f"DisplayConsts(top={self.top}, bottom={self.bottom}, left={self.left}, right={self.right}, " \
                f"next_top={self.next_top}, next_bottom={self.next_bottom}, next_left={self.next_left}, " \
                f"next_right={self.next_right}, num_extra_rows={self.num_extra_rows})"
