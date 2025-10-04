import pygame
import threading
import queue
import sys
import random

command_queue = queue.Queue()
_running = False
_objects = []  # 描画オブジェクトを保持

# === 画像付きオブジェクト ===
class GiftSprite:
    def __init__(self, image_path, x, y):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -4)  # 上向きに飛ぶ

    def update(self):
        self.vy += 0.2  # 重力
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def start(width=1280, height=720, title="Gift Effect"):
    global _running
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    _running = True

    while _running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop()

        # コマンド処理
        while not command_queue.empty():
            cmd, args = command_queue.get()
            if cmd == "spawn_gift":
                image_path = args[0]
                x = random.randint(100, width - 100)
                y = height - 50
                _objects.append(GiftSprite(image_path, x, y))

        # 更新と描画
        screen.fill((20, 20, 20))
        for obj in list(_objects):
            obj.update()
            obj.draw(screen)
            if obj.rect.y > height:  # 画面外で削除
                _objects.remove(obj)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def stop():
    global _running
    _running = False


def run_async():
    thread = threading.Thread(target=start, daemon=True)
    thread.start()


def spawn_gift(image_path):
    """TikTokイベントから呼び出される"""
    command_queue.put(("spawn_gift", (image_path,)))
