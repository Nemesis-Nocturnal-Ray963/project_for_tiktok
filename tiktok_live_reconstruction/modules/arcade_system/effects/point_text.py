import arcade

class PointText:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.text = "POINT : 0"
        self.arc_text = arcade.Text(self.text, x, y, arcade.color.WHITE, 40,anchor_x="center", anchor_y="center")

    def update_text(self, point):
        self.text = f"POINT : {point}"
        self.arc_text.text = self.text

    def draw(self):
        self.arc_text.draw()
