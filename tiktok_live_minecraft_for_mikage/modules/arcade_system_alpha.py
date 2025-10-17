import arcade, pyglet,threading, queue, random
import ctypes
import multiprocessing
import math

arcade_queue = None
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


class LightBeam:
    def __init__(self, x, y, color, min_angle_deg, max_angle_deg, speed,beam_width = 100,alpha = 120,beam_length = 1920):
        self.origin = (x, y)  # 根元の座標
        self.color = color
        self.min_angle = math.radians(min_angle_deg)
        self.max_angle = math.radians(max_angle_deg)
        self.time = 0.0
        self.speed = speed
        self.beam_length = beam_length
        self.beam_width = beam_width
        self.layers = 122
        self.alpha = alpha

    def update(self, dt):
        self.time += dt * self.speed
        # サイン波で往復
        oscillation = (math.sin(self.time) + 1) / 2
        self.angle = self.min_angle + (self.max_angle - self.min_angle) * oscillation

    def draw(self):
        x, y = self.origin
        angle = self.angle
        r, g, b = self.color

        for i in range(self.layers):
            t = i / self.layers
            alpha = int(self.alpha * (1 - t)**2)
            width = self.beam_width * (0.5 + t)
            length = self.beam_length * (t * 0.9 + 0.1)

            dx = math.cos(angle)
            dy = math.sin(angle)

            back_left_x  = x - math.sin(angle) * width * 0.2
            back_left_y  = y + math.cos(angle) * width * 0.2
            back_right_x = x + math.sin(angle) * width * 0.2
            back_right_y = y - math.cos(angle) * width * 0.2
            tip_x = x + dx * length
            tip_y = y + dy * length
            tip_left_x  = tip_x - math.sin(angle) * width
            tip_left_y  = tip_y + math.cos(angle) * width
            tip_right_x = tip_x + math.sin(angle) * width
            tip_right_y = tip_y - math.cos(angle) * width

            arcade.draw_polygon_filled(
                [(back_left_x, back_left_y),
                 (back_right_x, back_right_y),
                 (tip_right_x, tip_right_y),
                 (tip_left_x, tip_left_y)],
                (r, g, b, alpha)
            )

class GiftSprite(arcade.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__(image_path, scale=0.5)
        self.center_x = x
        self.center_y = y
        self.vx = 0
        self.vy = 0
        self.dragging = False


    def update_motion(self, dt, gravity=0.05):
        if not self.dragging:
            self.vy -= gravity       # 月の重力（非常に弱い）
            self.center_x += self.vx * dt * 60
            self.center_y += self.vy * dt * 60
            self.vx *= 0.99
            self.vy *= 0.99

    def keep_in_bounds(self, width, height):
        margin = 50
        if self.center_x < margin:
            self.center_x = margin
            self.vx *= -0.6
        elif self.center_x > width - margin:
            self.center_x = width - margin
            self.vx *= -0.6

    def is_outside_bottom(self, height):
        return self.center_y < -100

class GiftWindow(arcade.View):
    """
    self.beams = [
    # 左下：ゆっくり大きく動くシアン光
    LightBeam(x=0, y=0, color=(0, 255, 255), min_angle_deg=0, max_angle_deg=90, speed=1.0)# ゆっくり往復# シアン,
    # 右下：速く狭い範囲で動くマゼンタ光
    LightBeam(x=720, y=0, color=(255, 0, 255),min_angle_deg=100, max_angle_deg=160, speed=2.2),   # マゼンタ # 高速往復
    # 中央下：黄緑光、広範囲で滑らかに
    LightBeam(x=360, y=0, color=(180, 255, 120), min_angle_deg=30, max_angle_deg=150, speed=1.3)
    ]
    """

    def __init__(self):
        super().__init__()
        self.sprite_list = arcade.SpriteList()
        self.frame_list = arcade.SpriteList()
        self.drag_target = None
        self.show_frame = False  # ← フラグ
        self.show_icosahedron = False  # ← new
        self.angle_x = 45
        self.angle_y = 45
        self.scale = 60
        self.vertices = create_icosahedron_vertices()
        self.faces = create_icosahedron_faces()
        self.icosahedron_offset_y = 360  # ← 中央より上に表示
        self.time_counter = 0.0

        self.beams = [
            LightBeam(0, 0, (0, 255, 255),  0, 90, 1.5),                # 左下
            LightBeam(720, 0, (0, 255, 255), 90, 180, 1.2),              # 右下
            LightBeam(720, 1280, (255, 0, 255), 180, 270, 0.9),              # 右上
            LightBeam(0, 1280, (255, 255, 0), 270, 360, 0.6),           # 左上
        ]

        arcade.schedule(self.check_queue, 1/60)  # 60fpsで確認
        self.background_color = (0, 0, 0, 0)
        # try:
        #     hwnd = getattr(self, "_hwnd", None)
        #     if hwnd:
        #         style = user32.GetWindowLongW(hwnd, -20)
        #         user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        #         user32.SetLayeredWindowAttributes(hwnd, 0, 255, 2)
        # except Exception as e:
        #     print("透過処理スキップ:", e)
        # self.circle = arcade.Sprite()
        # self.circle.position = self.center
        # self.sprite_list.append(self.circle)

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
                x = random.randint(100, self.width - 100)
                y = random.randint(self.height // 2, self.height - 100)
                sprite = GiftSprite(image_path, x, y)
                self.sprite_list.append(sprite)
                sprites.append(sprite)
            elif cmd == "show_frame":
                # print(str(args[0]))
                if args[0] == "deployment":
                    self.sprite_frame = arcade.Sprite("assets/images/frame/frame_1.png", scale=1)
                    self.sprite_frame.width = 720
                    self.sprite_frame.height = 1280
                    self.sprite_frame.center_x = self.width // 2
                    self.sprite_frame.center_y = self.height // 2
                    self.frame_list.append(self.sprite_frame)
                elif args[0] == "shutdown":
                    if self.sprite_frame in self.frame_list:
                        self.frame_list.remove(self.sprite_frame)
                    self.sprite_frame = None
            elif cmd == "spawn_Icosahedron":
                print("success...")
                if args[0] == "light up":
                    print("1337")
                    self.show_icosahedron = True
                elif args[0] == "light down":
                    print("31337")
                    self.show_icosahedron = False

    # --- マウス操作 ---
    def on_mouse_press(self, x, y, button, modifiers):
        for s in reversed(self.sprite_list):
            if s.collides_with_point((x, y)):
                s.dragging = True
                self.drag_target = s
                s.vx = 0
                s.vy = 0
                break

    def on_mouse_release(self, x, y, button, modifiers):
        if self.drag_target:
            self.drag_target.dragging = False
            self.drag_target = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.drag_target:
            s = self.drag_target
            s.center_x += dx
            s.center_y += dy
            s.vx = dx / 2
            s.vy = dy / 2

    # def draw_light_beam(self):
    #     # --- 基本パラメータ ---
    #     x, y = self.light_pos
    #     beam_length = 1200          # 光の長さ
    #     beam_width = 100           # 開き幅
    #     layers = 122                # グラデーション層数
    #     base_alpha = 122           # 中心の透明度
    #     angle = self.beam_angle    # 現在の角度 (ラジアン)
    #     base_color = self.light_color

    #     # --- 各層を順に描画 ---
    #     for i in range(layers):
    #         t = i / layers
    #         alpha = int(base_alpha * 0.6 * (1 - t)**2)

    #         # --- ここが変更ポイント ---
    #         # tが進むほど先端を太くする
    #         width = beam_width * (0.5 + t)       # ← 先に行くほど広がる
    #         length = beam_length * (t * 0.9 + 0.1)  # ← 奥方向に進む

    #         dx = math.cos(angle)
    #         dy = math.sin(angle)

    #         # 手前（細い）
    #         back_left_x  = x - math.sin(angle) * width * 0.2
    #         back_left_y  = y + math.cos(angle) * width * 0.2
    #         back_right_x = x + math.sin(angle) * width * 0.2
    #         back_right_y = y - math.cos(angle) * width * 0.2

    #         # 先端（太い）
    #         tip_x = x + dx * length
    #         tip_y = y + dy * length
    #         tip_left_x  = tip_x - math.sin(angle) * width
    #         tip_left_y  = tip_y + math.cos(angle) * width
    #         tip_right_x = tip_x + math.sin(angle) * width
    #         tip_right_y = tip_y - math.cos(angle) * width

    #         # 4頂点で台形を描く
    #         arcade.draw_polygon_filled(
    #             [(back_left_x, back_left_y),
    #             (back_right_x, back_right_y),
    #             (tip_right_x, tip_right_y),
    #             (tip_left_x, tip_left_y)],
    #             (base_color[0], base_color[1], base_color[2], alpha)
    #         )

    # def draw_light(self):
    #     x, y = self.light_pos
    #     base_r, base_g, base_b = self.light_color
    #     layers = 255               # 円を重ねる層の数（多いほど滑らか）
    #     max_radius = self.light_radius + 400
    #     for i in range(layers):
    #         # 0.0～1.0 に正規化した割合
    #         t = i / layers
    #         # 半径とアルファを線形に減衰
    #         radius = self.light_radius + t * (max_radius - self.light_radius)
    #         alpha = int(self.light_alpha * (1 - t)**2)  # 二次減衰で柔らかく
    #         arcade.draw_circle_filled(x, y, radius, (base_r, base_g, base_b, alpha))


    def on_update(self, dt):
        # for s in list(sprites):
        #     s.update()

        for s in list(self.sprite_list):
            s.update_motion(dt)
            s.keep_in_bounds(self.width, self.height)
            if s.is_outside_bottom(self.height):
                s.remove_from_sprite_lists()

        if not self.show_icosahedron:
            return
        self.angle_x += dt * 0.0
        self.angle_y += dt * 1.0

        for beam in self.beams:
            beam.update(dt)



    def on_draw(self):
        self.clear()

        if self.show_icosahedron:
            # cx, cy = self.width // 2, self.height // 2 + self.icosahedron_offset_y
            # # 光源の方向（斜め上から）(0, 0, 1) に近いほど真上からの照明、(1, 0, 0) に近いほど横からの照明。
            # self.time_counter += 0.001
            # t = self.time_counter
            # lx = math.cos(t * 0.7)
            # ly = math.sin(t * 0.5)
            # lz = 0.8
            # light_len = math.sqrt(lx**2 + ly**2 + lz**2)
            # lx /= light_len
            # ly /= light_len
            # lz /= light_len
            
            # for face in self.faces:
            #     pts_2d = []
            #     pts_3d = []
            #     for i in face:
            #         x, y, z = self.vertices[i]
            #         x, y, z = rotate_point_3d(x, y, z, self.angle_x, self.angle_y)
            #         pts_2d.append((cx + x * self.scale, cy + y * self.scale))
            #         pts_3d.append((x, y, z))

            #     # 法線ベクトルを計算（2つの辺の外積）
            #     (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = pts_3d
            #     ux, uy, uz = (x2 - x1, y2 - y1, z2 - z1)
            #     vx, vy, vz = (x3 - x1, y3 - y1, z3 - z1)
            #     nx, ny, nz = (uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx)

            #     # 法線を正規化
            #     n_len = math.sqrt(nx**2 + ny**2 + nz**2)
            #     if n_len == 0:
            #         continue
            #     nx /= n_len
            #     ny /= n_len
            #     nz /= n_len

            #     # 光との角度（内積）
            #     dot = max(0, nx*lx + ny*ly + nz*lz)

            #     base = 160  # 基本の明るさ
            #     brightness = int(base + 95 * dot)
            #     brightness = max(60, min(255, brightness))
            #     color = (brightness, brightness, brightness)
            #     arcade.draw_polygon_filled(pts_2d, color)
                
            for beam in self.beams:
                beam.draw()



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
