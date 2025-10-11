import arcade, pyglet, threading, queue, random
import ctypes
arcade_queue = queue.Queue()
sprites = []

class GiftSprite(arcade.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__(image_path, scale=0.5)
        self.center_x = x
        self.center_y = y
        self.change_x = random.uniform(-3, 3)
        self.change_y = random.uniform(4, 8)

    def update(self):
        self.change_y -= 0.2
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.center_y < -100:
            sprites.remove(self)

class GiftWindow(arcade.Window):
    def __init__(self, width=540, height=960, title="Gift Effect"):
        # config = pyglet.gl.Config(double_buffer=True, alpha_size=8)
        # super().__init__(width, height, title, config=config, style="none", resizable=False)
        super().__init__(width, height, title, resizable=False)
        self.set_location(100, 100)
        arcade.set_background_color((0, 0, 0, 0)) # 背景を透明に
        self.sprite_list = arcade.SpriteList()
        arcade.schedule(self.check_queue, 1/30)

        hwnd = self._window_handle
        # hwnd = self.get_system_handle()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2)

    def check_queue(self, dt):
        while not arcade_queue.empty():
            cmd, args = arcade_queue.get()
            if cmd == "spawn_gift":
                image_path = args[0]
                x = random.randint(100, self.width - 100)
                y = random.randint(self.height // 2, self.height - 100)
                sprite = GiftSprite(image_path, x, y)
                self.sprite_list.append(sprite)
                sprites.append(sprite)

    def on_update(self, dt):
        for s in list(sprites):
            s.update()

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()

def run():
    window = GiftWindow()
    arcade.run()

def run_async():
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def spawn_gift(image_path):
    arcade_queue.put(("spawn_gift", (image_path,)))
