#!/usr/bin/env python3
"""Python 粒子圣诞树。运行动画，或导出可独立转发的 HTML 贺卡。"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAU = math.tau
PALETTES = ((255, 157, 201), (255, 204, 116), (139, 215, 255))
DEFAULT_WISH = "愿所有美好，都如期而至。\n愿你的冬天，有光，也有温暖。"
DEFAULT_NAME = "送给特别的你 ♡"


@dataclass(frozen=True)
class Particle:
    x: float
    y: float
    z: float
    brightness: float
    phase: float
    size: float = 1.0


def make_tree(count: int = 11500, seed: int = 25) -> list[Particle]:
    """生成填充粒子与九圈螺旋灯带；固定种子便于复现。"""
    rng = random.Random(seed)
    points = []
    for i in range(count):
        spiral = i < count * 0.66
        u = rng.random()
        height = u ** (1.35 if spiral else 1.6)
        wave = max(0, math.sin((height * 5.8 + 0.15) * TAU))
        radius = (1 - height) ** 1.08 * (2.8 + wave * 0.72)
        angle = u * 9 * TAU + rng.uniform(-0.14, 0.14) if spiral else rng.random() * TAU
        radius *= rng.uniform(0.91, 1.06) if spiral else math.sqrt(rng.random())
        points.append(Particle(
            math.cos(angle) * radius, height * 10, math.sin(angle) * radius,
            rng.uniform(0.45, 0.92) if spiral else rng.uniform(0.15, 0.48),
            rng.random() * TAU, rng.uniform(0.65, 1.35),
        ))
    return points


def make_ground(count: int = 1900) -> list[Particle]:
    rng = random.Random(12)
    points = []
    for i in range(count):
        angle = rng.random() * TAU
        radius = (3.4, 4.1, 4.9, 5.8)[i % 4] + rng.uniform(-0.07, 0.07)
        points.append(Particle(math.cos(angle) * radius, -0.16,
                               math.sin(angle) * radius, 0.3, rng.random() * TAU))
    return points


def project(point: Particle, angle: float, center: float, base: float,
            scale: float) -> tuple[int, int, float]:
    cosine, sine = math.cos(angle), math.sin(angle)
    x = point.x * cosine - point.z * sine
    z = point.x * sine + point.z * cosine
    perspective = 19 / (19 + z)
    return (round(center + x * scale * perspective),
            round(base - (point.y + z * 0.23) * scale * perspective), perspective)


def export_html(output: Path, wish: str, name: str, theme: int) -> Path:
    """将祝福嵌入独立 HTML。无网络依赖，也不需要安装 Pygame。"""
    template = (ROOT / "index.html").read_text(encoding="utf-8")
    config = json.dumps({"wish": wish, "name": name, "theme": theme}, ensure_ascii=False)
    # 防止祝福中的 </script> 被 HTML 解析器当作脚本结束标签。
    config = config.replace("<", "\\u003c")
    pattern = r'(<script id="card-config" type="application/json">).*?(</script>)'
    html, replacements = re.subn(pattern, lambda m: m[1] + config + m[2], template,
                                 count=1, flags=re.DOTALL)
    if replacements != 1:
        raise ValueError("HTML 分享模板缺少 card-config 配置")
    output = output.expanduser().resolve()
    if output == (ROOT / "index.html").resolve():
        raise ValueError("请选择其他输出文件名，以保留原始 HTML 分享模板")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output


def run_animation(wish: str, name: str, theme: int) -> None:
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("请先运行：python -m pip install -r requirements.txt\n"
                         "仅导出分享文件可直接运行：python tree.py --export 圣诞树.html") from exc

    pygame.init()
    try:
        screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
        pygame.display.set_caption("一棵圣诞树 · Python | 拖动旋转 · E 导出 HTML")
        clock = pygame.time.Clock()
        title_font = pygame.font.SysFont("Georgia", 53, italic=True)
        font = pygame.font.SysFont("PingFang SC,Microsoft YaHei,SimHei,Noto Sans CJK SC,Arial", 19)
        small_font = pygame.font.SysFont("PingFang SC,Microsoft YaHei,SimHei,Noto Sans CJK SC,Arial", 14)
        tree, ground = make_tree(), make_ground()
        rng = random.Random(1225)
        stars = [(rng.random(), rng.random(), rng.uniform(0.3, 1.0), rng.random() * TAU)
                 for _ in range(120)]
        snow = [[rng.random(), rng.random(), rng.uniform(0.015, 0.05), rng.uniform(1, 3)]
                for _ in range(65)]
        angle = elapsed = 0.0
        paused = dragging = False
        snow_on = True
        running = True
        status, status_until = "", 0
        while running:
            dt = min(clock.tick(60) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((max(600, event.w), max(480, event.h)), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dragging = True
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging = False
                elif event.type == pygame.MOUSEMOTION and dragging:
                    angle += event.rel[0] * 0.009
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_t:
                        theme = (theme + 1) % len(PALETTES)
                    elif event.key == pygame.K_s:
                        snow_on = not snow_on
                    elif event.key == pygame.K_e:
                        try:
                            path = export_html(Path.cwd() / "送你一棵圣诞树.html", wish, name, theme)
                            status = "已导出：" + str(path)
                            print(status)
                        except (OSError, ValueError) as exc:
                            status = "导出失败：" + str(exc)
                        status_until = pygame.time.get_ticks() + 6000
            if not paused:
                elapsed += dt
                angle += dt * 0.22
            width, height = screen.get_size()
            center, base = width * 0.65, height * 0.81
            scale = min(height * 0.055, width * 0.049)
            color = PALETTES[theme]
            screen.fill((8, 9, 18))
            for x, y, brightness, phase in stars:
                value = round(45 + 90 * brightness * (0.5 + 0.5 * math.sin(elapsed * 0.6 + phase)))
                pygame.draw.circle(screen, (value, value, min(255, value + 15)),
                                   (round(x * width), round(y * height)), 1)
            # 发光层以加色混合叠加，让明亮灯点周围有柔和光晕。
            lights = pygame.Surface((width, height))
            for point in ground + tree:
                x, y, perspective = project(point, angle, center, base, scale)
                if not (0 <= x < width and 0 <= y < height):
                    continue
                brightness = point.brightness * (0.7 + 0.3 * math.sin(elapsed * 1.7 + point.phase))
                tint = tuple(round(channel * brightness) for channel in color)
                radius = max(1, round(point.size * perspective))
                pygame.draw.circle(screen, tint, (x, y), radius)
                if point.brightness > 0.87:
                    for extra, strength in ((4, 0.035), (2, 0.08)):
                        pygame.draw.circle(lights, tuple(round(c * strength) for c in color),
                                           (x, y), radius + extra)
            top_x, top_y, _ = project(Particle(0, 10.65, 0, 1, 0), angle, center, base, scale)
            heart = []
            for i in range(170):
                a = i / 170 * TAU
                k = scale * 0.033 * (1 + math.sin(elapsed * 2) * 0.045)
                x = 16 * math.sin(a) ** 3
                y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
                heart.append((round(top_x + x * k), round(top_y - y * k)))
            pygame.draw.aalines(screen, color, True, heart)
            screen.blit(lights, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            if snow_on:
                for flake in snow:
                    if not paused:
                        flake[1] += dt * flake[2]
                        if flake[1] > 1.04:
                            flake[1], flake[0] = -0.04, rng.random()
                    pygame.draw.circle(screen, (155, 149, 168),
                                       (round(flake[0] * width), round(flake[1] * height)), round(flake[3]))
            left, top = round(width * 0.08), round(height * 0.33)
            screen.blit(small_font.render("A LITTLE CHRISTMAS MAGIC", True, color), (left, top - 45))
            for i, line in enumerate(("Merry", "Christmas")):
                screen.blit(title_font.render(line, True, (247, 233, 238)), (left, top + i * 61))
            text_y = top + 150
            # Python 桌面版按字符折行，避免长祝福遮住树身。
            max_width = round(width * 0.30)
            for paragraph in wish.split("\n"):
                line = ""
                for character in paragraph:
                    if line and font.size(line + character)[0] > max_width:
                        screen.blit(font.render(line, True, (201, 185, 197)), (left, text_y))
                        text_y += 29
                        line = ""
                    line += character
                screen.blit(font.render(line, True, (201, 185, 197)), (left, text_y))
                text_y += 29
            screen.blit(font.render(name, True, color), (left, text_y + 15))
            controls = "空格 暂停/继续   T 配色   S 飘雪   E 导出 HTML   Esc 退出"
            screen.blit(small_font.render(controls, True, (165, 145, 161)), (left, height - 38))
            if pygame.time.get_ticks() < status_until:
                screen.blit(small_font.render(status, True, color), (left, height - 65))
            pygame.display.flip()
    finally:
        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wish", default=DEFAULT_WISH, help="自定义祝福语")
    parser.add_argument("--name", default=DEFAULT_NAME, help="自定义署名")
    parser.add_argument("--theme", type=int, choices=range(3), default=0,
                        help="0 绯樱 / 1 鎏金 / 2 冰蓝")
    parser.add_argument("--export", type=Path, metavar="FILE.html",
                        help="只生成离线 HTML 贺卡，不启动动画，也不需要 Pygame")
    args = parser.parse_args()
    if len(args.wish) > 60 or len(args.name) > 20:
        parser.error("祝福语最多 60 字，署名最多 20 字")
    if args.export:
        try:
            print("已导出：", export_html(args.export, args.wish, args.name, args.theme))
        except (OSError, ValueError) as exc:
            parser.exit(1, f"导出失败：{exc}\n")
    else:
        run_animation(args.wish, args.name, args.theme)


if __name__ == "__main__":
    main()
