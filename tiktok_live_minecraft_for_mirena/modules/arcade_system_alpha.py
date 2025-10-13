import arcade, pyglet,threading, queue, random
import ctypes
import multiprocessing
import math

arcade_queue = None
# arcade_queue = multiprocessing.Queue()
sprites = []

def create_icosahedron_vertices():
    phi = (1 + math.sqrt(5)) / 2
    v = [(-1,  phi,  0), ( 1,  phi,  0), (-1, -phi,  0), ( 1, -phi,  0),
            ( 0, -1,  phi), ( 0,  1,  phi), ( 0, -1, -phi), ( 0,  1, -phi),
            ( phi,  0, -1), ( phi,  0,  1), (-phi,  0, -1), (-phi,  0,  1)]
    return v

def create_icosahedron_faces():
    return [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
    ]

def rotate_point_3d(x, y, z, ax, ay):
    y2 = y * math.cos(ax) - z * math.sin(ax)
    z2 = y * math.sin(ax) + z * math.cos(ax)
    x3 = x * math.cos(ay) + z2 * math.sin(ay)
    z3 = -x * math.sin(ay) + z2 * math.cos(ay)
    return x3, y2, z3


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
        self.show_icosahedron = False  # ← new
        self.angle_x = 0
        self.angle_y = 0
        self.scale = 60
        self.vertices = create_icosahedron_vertices()
        self.faces = create_icosahedron_faces()
        self.icosahedron_offset_y = 360  # ← 中央より上に表示




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
            elif cmd == "show_frame":
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
            elif cmd == "spawn_Icosahedron":
                print("success...")
                if args[0]:
                    self.show_icosahedron = True
                else:
                    self.show_icosahedron = False







    def on_update(self, dt):
        for s in list(sprites):
            s.update()

        if self.show_icosahedron:
            self.angle_x += dt * 0.1
            self.angle_y += dt * 1.2
    def on_draw(self):
        self.clear()


        if self.show_icosahedron:
            cx, cy = self.width // 2, self.height // 2 + self.icosahedron_offset_y
            
            
            # 光源の方向（斜め上から）(0, 0, 1) に近いほど真上からの照明、(1, 0, 0) に近いほど横からの照明。
            light_dir = (0.4, 0.0, 1.0)
            lx, ly, lz = light_dir
            light_len = math.sqrt(lx**2 + ly**2 + lz**2)
            lx /= light_len
            ly /= light_len
            lz /= light_len
            
            for face in self.faces:
                pts_2d = []
                pts_3d = []
                for i in face:
                    x, y, z = self.vertices[i]
                    x, y, z = rotate_point_3d(x, y, z, self.angle_x, self.angle_y)
                    pts_2d.append((cx + x * self.scale, cy + y * self.scale))
                    pts_3d.append((x, y, z))

                # 法線ベクトルを計算（2つの辺の外積）
                (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = pts_3d
                ux, uy, uz = (x2 - x1, y2 - y1, z2 - z1)
                vx, vy, vz = (x3 - x1, y3 - y1, z3 - z1)
                nx, ny, nz = (uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx)

                # 法線を正規化
                n_len = math.sqrt(nx**2 + ny**2 + nz**2)
                if n_len == 0:
                    continue
                nx /= n_len
                ny /= n_len
                nz /= n_len

                # 光との角度（内積）
                dot = max(0, nx*lx + ny*ly + nz*lz)

                base = 160  # 基本の明るさ
                brightness = int(base + 95 * dot)
                brightness = max(60, min(255, brightness))
                color = (brightness, brightness, brightness)
                arcade.draw_polygon_filled(pts_2d, color)





        self.sprite_list.draw()
        self.frame_list.draw()
def run(shared_queue):
    # Create a window class. This is what actually shows up on screen
    global arcade_queue
    arcade_queue = shared_queue
    window = arcade.Window(720, 1280, "Gift Effect")

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
