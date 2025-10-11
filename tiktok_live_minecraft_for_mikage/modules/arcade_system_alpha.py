import arcade, threading, queue, random
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
        super().__init__(width, height, title, resizable=False)
        self.set_location(100, 100)
        transparent_color = arcade.color.TRANSPARENT_BLACK
        self.background_color = transparent_color
        arcade.set_background_color(transparent_color)
        self.sprite_list = arcade.SpriteList()
        arcade.schedule(self.check_queue, 1/30)
        hwnd = self._resolve_window_handle()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2)

    def _resolve_window_handle(self):
        """Return the native HWND for the underlying Pyglet window."""
        if hasattr(self, "_window_handle"):
            return self._window_handle

        handle_getters = (
            getattr(self, "get_system_handle", None),
            getattr(self, "_hwnd", None),
        )

        for getter in handle_getters:
            if getter is None:
                continue
            try:
                return getter() if callable(getter) else getter
            except Exception:
                continue

        canvas = getattr(self, "canvas", None)
        if canvas is not None:
            hwnd = getattr(canvas, "hwnd", None)
            if hwnd is not None:
                return hwnd
            handle = getattr(canvas, "get_handle", None)
            if callable(handle):
                try:
                    return handle()
                except Exception:
                    pass

        raise AttributeError("GiftWindow could not determine native window handle")
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
        self.clear(color=self.background_color)
        self.sprite_list.draw()

def run():
    window = GiftWindow()
    arcade.run()

def run_async():
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def spawn_gift(image_path):
    arcade_queue.put(("spawn_gift", (image_path,)))
