# modules/arcade_system/effects/beams.py
# ==============================================
# 光ビーム系エフェクト
# 役割：
#  - GPU(GLSL)を用いた加算ブレンド光描画
#  - LightBeamクラスのupdate/draw制御
#  - Icosahedronなどの光演出切替
# ==============================================

import arcade
import math
import array


class LightBeam:
    """光線エフェクト（GLSLベース）"""
    def __init__(self, x, y, color, min_angle, max_angle, speed, width=100, alpha=120, length=1280):
        self.origin = (x, y)
        self.color = color
        self.min_angle = math.radians(min_angle)
        self.max_angle = math.radians(max_angle)
        self.angle = self.min_angle
        self.speed = speed
        self.time = 0.0
        self.beam_length = length
        self.beam_width = width
        self.alpha = alpha

    def update(self, dt):
        """角度を時間に応じて往復変化"""
        self.time += dt * self.speed
        t = (math.sin(self.time) + 1) / 2
        self.angle = self.min_angle + (self.max_angle - self.min_angle) * t

    def draw(self, ctx, prog, geo):
        """GPU描画（blendは呼び出し側で設定）"""
        W, H = float(ctx.window.width), float(ctx.window.height)
        ox, oy = self.origin
        ang = self.angle
        r, g, b = [c / 255.0 for c in self.color]
        a = self.alpha / 255.0

        prog["u_resolution"] = (W, H)
        prog["u_origin"] = (ox, oy)
        prog["u_dir"] = (math.cos(ang), math.sin(ang))
        prog["u_length"] = float(self.beam_length)
        prog["u_width"] = float(self.beam_width * 0.5)
        prog["u_color"] = (r, g, b, a)

        geo.render(prog)


# --- GLSL初期化・制御 ---
class BeamManager:
    """複数の光線をまとめて管理"""
    def __init__(self, window):
        self.window = window
        self.beams: list[LightBeam] = []
        self._gl_ready = False
        self._prog = None
        self._geo = None

    def _init_gl(self):
        """GLSLシェーダ・ジオメトリ初期化"""
        if self._gl_ready:
            return
        ctx = self.window.window.ctx
        vert = """
        #version 330
        in vec2 in_pos;
        out vec2 v_uv;
        void main(){
            v_uv = (in_pos + 1.0) * 0.5;
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
            float t = dot(p, u_dir);
            float d = abs(cross2(p, u_dir));

            float dyn_w = u_width * (1.0 + t / u_length * 1.5);
            float inside = step(0.0, t) * step(t, u_length);
            float edge = smoothstep(dyn_w * 0.6, dyn_w, d);
            float mask = inside * (1.0 - edge);

            if (mask <= 0.001) discard;
            float fade = smoothstep(u_length, 0.0, t);
            mask *= fade;

            float core = exp(-pow(d / (dyn_w * 0.3), 2.0));
            vec3 col = mix(u_color.rgb * 0.5, u_color.rgb, core) * mask * fade;
            float alpha = u_color.a * mask * fade * (0.6 + core * 0.4);
            outColor = vec4(col, alpha);
        }
        """
        prog = ctx.program(vertex_shader=vert, fragment_shader=frag)
        quad = array.array("f", [-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1])
        vbo = ctx.buffer(data=quad.tobytes())
        geo = ctx.geometry([arcade.gl.BufferDescription(vbo, "2f", ("in_pos",))])
        self._prog, self._geo = prog, geo
        self._gl_ready = True

    def update(self, dt):
        for b in self.beams:
            b.update(dt)

    def draw(self):
        """加算ブレンドで全ビームを描画"""
        if not self.beams:
            return
        if not self._gl_ready:
            self._init_gl()
        ctx = self.window.window.ctx
        ctx.enable_only("blend")
        ctx.blend_equation = "FUNC_ADD"
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE
        for b in self.beams:
            b.draw(ctx, self._prog, self._geo)


# --- コマンド関数 ---
def toggle_icosahedron(args: list, window):
    """
    光演出のON/OFFトグル
    args[0] = "light up" または "light down"
    """
    if not hasattr(window, "beam_manager"):
        window.beam_manager = BeamManager(window)

        # 初期構成：四隅の光
        window.beam_manager.beams = [
            LightBeam(0, 0, (0, 255, 255), 0, 90, 1.5, 100, 120, 1440),
            LightBeam(720, 0, (0, 255, 255), 90, 180, 1.2, 100, 120, 1440),
            LightBeam(720, 1280, (255, 0, 255), 180, 270, 0.9, 100, 120, 1440),
            LightBeam(0, 1280, (255, 255, 0), 270, 360, 0.6, 100, 120, 1440),
        ]

    if args and args[0] == "light up":
        if window.beam_manager not in window.layers["light"]:
            window.layers["light"].append(window.beam_manager)
        # window.effects.append(window.beam_manager)
            print("[ARC-BEAM] Light up")
    elif args and args[0] == "light down":
        if window.beam_manager in window.layers["light"]:
            window.layers["light"].remove(window.beam_manager)
            print("[ARC-BEAM] Light down")
