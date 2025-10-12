import arcade, pyglet,threading, queue, random
import ctypes
import multiprocessing
import math

arcade_queue = None
# arcade_queue = multiprocessing.Queue()
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
            self.remove_from_sprite_lists()

class GiftWindow(arcade.View):
    def __init__(self):
        super().__init__()
        self.sprite_list = arcade.SpriteList()
        self.frame_list = arcade.SpriteList()
        self.show_frame = False  # ← フラグ
        
        arcade.schedule(self.check_queue, 1/60)  # 60fpsで確認
        
        self.background_color = (0, 0, 0, 0)
        try:
            hwnd = getattr(self, "_hwnd", None)
            if hwnd:
                style = user32.GetWindowLongW(hwnd, -20)
                user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
                user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2)
        except Exception as e:
            print("透過処理スキップ:", e)
        self.circle = arcade.Sprite()
        self.circle.position = self.center
        self.sprite_list.append(self.circle)

    def check_queue(self, dt):
        # print("boot now...")
        queue_size = arcade_queue.qsize()
        if queue_size == 0:
            return  # 何もなければ終了
        for _ in range(queue_size):
            try:
                cmd, args = arcade_queue.get_nowait()
            except Exception:
                break  # 空になったら安全に抜ける

            print(args)
            if cmd == "spawn_gift":
                image_path = args[0]
                # sprite = GiftSprite(image_path, self.width/2, self.height/2)
                # self.sprite_list.append(sprite)
                x = random.randint(100, self.width - 100)
                y = random.randint(self.height // 2, self.height - 100)
                sprite = GiftSprite(image_path, x, y)
                self.sprite_list.append(sprite)
                sprites.append(sprite)
            if cmd == "show_frame":
                print(str(args[0]))
                if args[0]:
                    self.sprite_frame = arcade.Sprite("assets/images/frame/frame_1.png", scale=1)
                    self.sprite_frame.width = 720
                    self.sprite_frame.height = 1280
                    self.sprite_frame.center_x = self.width // 2
                    self.sprite_frame.center_y = self.height // 2
                    self.frame_list.append(self.sprite_frame)
                else:
                    if hasattr(self, "sprite_frame") and self.sprite_frame in self.frame_list:
                        self.frame_list.remove(self.sprite_frame)

    def on_update(self, dt):
        for s in list(sprites):
            s.update()

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()
        self.frame_list.draw()

def run(shared_queue):
    # Create a window class. This is what actually shows up on screen
    global arcade_queue
    arcade_queue = shared_queue
    window = arcade.Window(720, 1280, "Minimal SPrite Example")

    # Create and setup the GameView

    game = GiftWindow()

    # Show GameView on screen

    window.show_view(game)

    # Start the arcade game loop

    arcade.run()


def run_async():
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def spawn_gift(image_path):
    arcade_queue.put(("spawn_gift", (image_path,)))
