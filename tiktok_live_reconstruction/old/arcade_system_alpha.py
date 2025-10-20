import arcade, pyglet,threading, queue, random
import ctypes
import multiprocessing
import math
import array
from arcade.hitbox import SimpleHitBoxAlgorithm
import os

from pyglet.gl import glEnable, glBlendFunc, glBlendEquation,glIsEnabled,GL_BLEND, GL_FUNC_ADD, GL_SRC_ALPHA, GL_ONE

# ==== 外部から main.py が代入 ====
arcade_queue: queue.Queue | None = None

class LightBeam:
    def __init__(self, x, y, color, min_angle_deg, max_angle_deg, speed,beam_width = 100,alpha = 120,beam_length = 1280):
        self.origin = (x, y)  # 根元の座標
        self.color = color
        self.min_angle = math.radians(min_angle_deg)
        self.max_angle = math.radians(max_angle_deg)
        self.angle = self.min_angle
        self.time = 0.0
        self.speed = speed
        self.beam_length = beam_length
        self.beam_width = beam_width
        # self.layers = 122
        self.alpha = alpha

    def update(self, dt):
        self.time += dt * self.speed
        # サイン波で往復
        oscillation = (math.sin(self.time) + 1) / 2
        self.angle = self.min_angle + (self.max_angle - self.min_angle) * oscillation

    # def draw(self):
    #     x, y = self.origin
    #     angle = self.angle
    #     r, g, b = self.color

    #     for i in range(self.layers):
    #         t = i / self.layers
    #         alpha = int(self.alpha * (1 - t)**2)
    #         width = self.beam_width * (0.5 + t)
    #         length = self.beam_length * (t * 0.9 + 0.1)

    #         dx = math.cos(angle)
    #         dy = math.sin(angle)

    #         back_left_x  = x - math.sin(angle) * width * 0.2
    #         back_left_y  = y + math.cos(angle) * width * 0.2
    #         back_right_x = x + math.sin(angle) * width * 0.2
    #         back_right_y = y - math.cos(angle) * width * 0.2
    #         tip_x = x + dx * length
    #         tip_y = y + dy * length
    #         tip_left_x  = tip_x - math.sin(angle) * width
    #         tip_left_y  = tip_y + math.cos(angle) * width
    #         tip_right_x = tip_x + math.sin(angle) * width
    #         tip_right_y = tip_y - math.cos(angle) * width

    #         arcade.draw_polygon_filled(
    #             [(back_left_x, back_left_y),
    #              (back_right_x, back_right_y),
    #              (tip_right_x, tip_right_y),
    #              (tip_left_x, tip_left_y)],
    #             (r, g, b, alpha)
    #         )

class GiftSprite(arcade.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__(image_path, scale=0.5)
        self.center_x = x
        self.center_y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.dragging = False
        # 衝突用ヒットボックス（矩形）

    def update_motion(self, dt, gravity=0.05):
        if not self.dragging:
            self.vy -= gravity       # 月の重力（非常に弱い）
            self.center_x += self.vx * dt * 60
            self.center_y += self.vy * dt * 60
            self.vx *= 0.99
            self.vy *= 0.99

    def keep_in_bounds(self, width, height):
        margin = 110
        if self.center_x < margin:
            self.center_x = margin
            self.vx *= -0.6
        elif self.center_x > width - margin:
            self.center_x = width - margin
            self.vx *= -0.6

    def is_outside_bottom(self, height):
        return self.center_y < -100

class GiftWindow(arcade.View):
    # path = r"C:\Users\x701c\project_for_tiktok\tiktok_live_reconstruction\assets\images\gift\whale_diving.png"
    # print(arcade.load_texture(path))
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
        # self.angle_x = 45
        # self.angle_y = 45
        # self.scale = 60
        # self.vertices = create_icosahedron_vertices()
        # self.faces = create_icosahedron_faces()
        # self.icosahedron_offset_y = 360  # ← 中央より上に表示
        self.time_counter = 0.0

        self.beams = [
            # LightBeam(0, 0, (0, 255, 255),  0, 90, 0.3,100,120,1500),                # test
            # LightBeam(720, 0, (255, 0, 255),  90, 180, 0.3,100,120,1500),                # test
            LightBeam(0, 0, (0, 255, 255),  0, 90, 1.5,100,120,1440),                # 左下
            LightBeam(720, 0, (0, 255, 255), 90, 180, 1.2,100,120,1440),              # 右下
            LightBeam(720, 1280, (255, 0, 255), 180, 270, 0.9,100,120,1440),              # 右上
            LightBeam(0, 1280, (255, 255, 0), 270, 360, 0.6,100,120,1440),           # 左上
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
        self._gl_ready = False
        self._gl_prog = None
        self._gl_geo = None
        self._blit_prog = None
        self._beam_buffer = None

    def _init_gl(self):
        if self._gl_ready:
            return
        ctx = self.window.ctx  # arcade.gl のコンテキスト
        vert = """
        #version 330
        in vec2 in_pos;
        out vec2 v_uv;
        void main(){
            v_uv = (in_pos + 1.0) * 0.5;         // [-1,1] → [0,1]
            gl_Position = vec4(in_pos, 0.0, 1.0);
        }
        """
        frag = """
        #version 330
        in vec2 v_uv;
        out vec4 outColor;

        uniform vec2 u_resolution;
        uniform vec2 u_origin;
        uniform vec2 u_dir;
        uniform float u_length;
        uniform float u_width;
        uniform vec4 u_color;

        float cross2(vec2 a, vec2 b){ return a.x*b.y - a.y*b.x; }

        void main(){
            vec2 frag = v_uv * u_resolution;
            vec2 p = frag - u_origin;

            // 軸方向成分
            float t = dot(p, u_dir);
            // 軸からの距離
            float d = abs(cross2(p, u_dir));

            // 扇形のような発散をつける（t に比例して幅を広げる）
            float dynamic_width = u_width * (1.0 + t / u_length * 1.5);
            // マスク生成
            float inside_len  = step(0.0, t) * step(t, u_length);
            float edge = smoothstep(dynamic_width * 0.6, dynamic_width, d);
            float mask = inside_len * (1.0 - edge);

            if (mask <= 0.001) discard;
            // 距離で減衰（先端に向かってフェード）
            float fade = smoothstep(u_length, 0.0, t);
            mask *= fade;

            // 少し中央が明るくなるようなコア光
            float core = exp(-pow(d / (dynamic_width * 0.3), 2.0));
            vec3 col = mix(u_color.rgb * 0.5, u_color.rgb, core) * mask * fade;

            // 透過アルファ：距離・中心に応じて透明度決定
            float alpha = u_color.a * mask * fade * (0.6 + core * 0.4);

            outColor = vec4(col, alpha);
        }
        """
                # 転送専用（バッファ内容を画面へ描く）
        blit_frag = """
        #version 330
        in vec2 v_uv;
        out vec4 outColor;
        uniform sampler2D u_tex;
        void main(){
            outColor = texture(u_tex, v_uv);
        }
        """
        self._gl_prog = self.window.ctx.program(vertex_shader=vert, fragment_shader=frag)
        self._blit_prog = ctx.program(vertex_shader=vert, fragment_shader=blit_frag)
        # フルスクリーンクアッド（NDC）

        quad = array.array('f', [-1,-1,  1,-1,  -1,1,   -1,1,  1,-1,  1,1])
        vbo = ctx.buffer(data=quad.tobytes())
        self._gl_geo = ctx.geometry([arcade.gl.BufferDescription(vbo, '2f', ('in_pos',))])

        self._beam_buffer = ctx.framebuffer(
            color_attachments=[ctx.texture((self.window.width, self.window.height))]
            )

        self._gl_ready = True


    def check_queue(self, dt):
        # print("receiver id:", id(arcade_queue))
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
                    # args[0] が 'assets/images/gift/xxx.png' の場合
                if not os.path.isabs(image_path):
                    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # プロジェクトルート
                    image_path = os.path.join(base, image_path)
                    image_path = os.path.abspath(image_path).replace("\\", "/")
                print("絶対パス変換:", image_path)
                x = random.randint(100, self.width - 100)
                y = random.randint(self.height // 2, self.height - 100)
                sprite = GiftSprite(image_path, x, y)
                self.sprite_list.append(sprite)
                print("[ARC] sprite append OK:", sprite)
            elif cmd == "show_frame":
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

    def on_update(self, dt):
        # for s in list(sprites):
        #     s.update()

        for s in list(self.sprite_list):
            s.update_motion(dt)
            s.keep_in_bounds(self.width, self.height)
            if s.is_outside_bottom(self.height):
                s.remove_from_sprite_lists()

        # --- 衝突チェック ---
        self.handle_collisions()

        if not self.show_icosahedron:
            return
        # self.angle_x += dt * 0.0
        # self.angle_y += dt * 1.0

        for beam in self.beams:
            beam.update(dt)

    def handle_collisions(self):
        """単純な反発式の当たり判定"""
        for i, s1 in enumerate(self.sprite_list):
            for s2 in self.sprite_list[i + 1:]:
                if arcade.check_for_collision(s1, s2):
                    dx = s1.center_x - s2.center_x
                    dy = s1.center_y - s2.center_y
                    dist = math.hypot(dx, dy)
                    if dist == 0:
                        continue
                    nx, ny = dx / dist, dy / dist  # 法線方向

                    # 反発ベクトル
                    overlap = 0.1 * (s1.width/2 + s2.width/2 - dist)
                    if overlap > 0:
                        s1.center_x += nx * overlap
                        s1.center_y += ny * overlap
                        s2.center_x -= nx * overlap
                        s2.center_y -= ny * overlap

                    # 速度の反発
                    s1.vx, s2.vx = s2.vx, s1.vx
                    s1.vy, s2.vy = s2.vy, s1.vy



    # 3) 既存の LightBeam を使って角度だけ更新し、描画はGPUに差し替え
    def _draw_beam_gl(self, beam):

        if not self._gl_ready:
            self._init_gl()


        ctx = self.window.ctx
        ctx.enable_only("blend")
        ctx.blend_equation = "FUNC_ADD"
        ctx.blend_func = ctx.SRC_ALPHA, ctx.SRC_ALPHA  # 加算

        self._beam_buffer.use()

        # 画面サイズ
        W, H = float(self.width), float(self.height)

        # 既存 LightBeam の状態を使う
        ox, oy = beam.origin
        ang = beam.angle                      # radians
        length = beam.beam_length
        width  = beam.beam_width * 0.5        # 半幅に
        r,g,b = [c/255.0 for c in beam.color]
        a = beam.alpha/255.0

        # uniforms
        prog = self._gl_prog
        prog['u_resolution'] = (W, H)
        prog['u_origin']     = (ox, oy)
        prog['u_dir']        = (math.cos(ang), math.sin(ang))
        prog['u_length']     = float(length)
        prog['u_width']      = float(width)
        prog['u_color']      = (r, g, b, a)

        self._gl_geo.render(prog)
        # self.window.ctx.blend_func = (arcade.gl.ONE, arcade.gl.ONE)
        # self.window.ctx.blend_equation = "FUNC_ADD"

    def on_draw(self):
        # print("[ARC DRAW]")
        from pyglet.gl import glEnable, glBlendFunc, glBlendEquation,glIsEnabled,GL_BLEND, GL_FUNC_ADD, GL_SRC_ALPHA, GL_ONE
        # print("Blend enabled:", glIsEnabled(GL_BLEND))
        ctx = self.window.ctx
        if not self._gl_ready:
            self._init_gl()
        # --- (1) バッファを初期化 ---

        # glEnable(GL_BLEND)
        # glBlendEquation(GL_FUNC_ADD)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        self._beam_buffer.use()
        self._beam_buffer.clear()
        ctx.enable_only("blend")
        ctx.blend_equation = "FUNC_ADD"
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE

        if self.show_icosahedron:
            for beam in self.beams:
                self._draw_beam_gl(beam)

            # 画面をターゲットに戻す
        ctx.screen.use()
        self.clear()

        # ビーム描画結果を転送
        self._beam_buffer.color_attachments[0].use(0)
        self._gl_geo.render(self._blit_prog)

        
        self.sprite_list.draw()
        self.frame_list.draw()
        
        


def run(shared_queue: queue.Queue):
    # Create a window class. This is what actually shows up on screen
    global arcade_queue
    arcade_queue = shared_queue
    window = arcade.Window(720, 1280, "Gift Effect", resizable=True, gl_version=(3, 3))
    window.clear_color = (0, 0, 0, 0)
    # Create and setup the GameView
    game = GiftWindow()
    # Show GameView on screen
    window.show_view(game)
    # Start the arcade game loop
    arcade.run()


# def run_async():
#     thread = threading.Thread(target=run, daemon=True)
#     thread.start()

# def spawn_gift(image_path):
#     arcade_queue.put(("spawn_gift", (image_path,)))
