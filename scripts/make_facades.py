# -*- coding: utf-8 -*-
"""Generate procedural facade textures for campus buildings, driven by real
campus photo characteristics: light stone walls, red-brick grilles, blue glass,
red dorm roofs. Each texture tiles over one building side."""
from PIL import Image, ImageDraw
import os

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'tex'))
os.makedirs(OUT, exist_ok=True)

W, H = 512, 512          # one tile = 24m wide x 12m high (2 floors)


def tex_classroom(path):
    """灰白石材墙 + 红褐色竖向格栅 + 蓝灰玻璃窗（官网照片特征）"""
    im = Image.new('RGB', (W, H), (214, 212, 205))
    d = ImageDraw.Draw(im)
    # subtle stone panel joints
    for x in range(0, W, 64):
        d.line((x, 0, x, H), fill=(198, 196, 190), width=1)
    for y in range(0, H, 128):
        d.line((0, y, W, y), fill=(198, 196, 190), width=1)
    # two floor bands (each 256px tall) -> 4 window bays per floor
    for fl in range(2):
        y0 = fl * 256
        # floor slab line
        d.rectangle((0, y0 + 250, W, y0 + 256), fill=(176, 174, 168))
        for bay in range(4):
            x0 = 16 + bay * 128
            # red brick grille panel (left part of bay)
            d.rectangle((x0, y0 + 40, x0 + 26, y0 + 210), fill=(150, 78, 66))
            for gy in range(y0 + 46, y0 + 210, 12):
                d.line((x0, gy, x0 + 26, gy), fill=(124, 60, 52), width=1)
            # window with blue glass + frame
            wx0, wx1 = x0 + 34, x0 + 118
            d.rectangle((wx0, y0 + 44, wx1, y0 + 206), fill=(70, 84, 96))
            d.rectangle((wx0 + 4, y0 + 48, wx1 - 4, y0 + 202), fill=(96, 132, 158))
            # glass reflection stripes
            d.polygon([(wx0 + 4, y0 + 202), (wx0 + 46, y0 + 48),
                       (wx0 + 74, y0 + 48), (wx0 + 32, y0 + 202)], fill=(120, 158, 184))
            d.line((wx0 + 2, y0 + 125, wx1 - 2, y0 + 125), fill=(58, 72, 84), width=3)
            # window sill
            d.rectangle((wx0 - 2, y0 + 206, wx1 + 2, y0 + 212), fill=(228, 226, 220))
    im.save(path)
    print(path)


def tex_office(path):
    """综合办公/科研楼：浅灰石材 + 通高蓝玻璃带 + 竖向金属分隔"""
    im = Image.new('RGB', (W, H), (206, 209, 210))
    d = ImageDraw.Draw(im)
    for fl in range(2):
        y0 = fl * 256
        d.rectangle((0, y0 + 252, W, y0 + 256), fill=(170, 175, 178))
        for bay in range(4):
            x0 = 12 + bay * 128
            d.rectangle((x0, y0 + 30, x0 + 108, y0 + 226), fill=(62, 82, 104))
            d.rectangle((x0 + 3, y0 + 34, x0 + 105, y0 + 222), fill=(92, 126, 154))
            d.polygon([(x0 + 3, y0 + 222), (x0 + 40, y0 + 34),
                       (x0 + 66, y0 + 34), (x0 + 28, y0 + 222)], fill=(118, 154, 182))
            d.line((x0 + 54, y0 + 30, x0 + 54, y0 + 226), fill=(52, 70, 90), width=3)
    im.save(path)
    print(path)


def tex_dorm(path):
    """宿舍：米黄色墙 + 蓝灰窗 + 每层阳台栏板（学生公寓特征）"""
    im = Image.new('RGB', (W, H), (222, 213, 190))
    d = ImageDraw.Draw(im)
    for fl in range(2):
        y0 = fl * 256
        d.rectangle((0, y0 + 250, W, y0 + 256), fill=(190, 182, 162))
        for bay in range(5):
            x0 = 10 + bay * 102
            # window
            d.rectangle((x0 + 8, y0 + 40, x0 + 76, y0 + 150), fill=(64, 80, 92))
            d.rectangle((x0 + 11, y0 + 43, x0 + 73, y0 + 147), fill=(104, 138, 162))
            # balcony slab + railing
            d.rectangle((x0, y0 + 168, x0 + 92, y0 + 178), fill=(206, 198, 178))
            for rx in range(x0 + 6, x0 + 92, 10):
                d.line((rx, y0 + 150, rx, y0 + 168), fill=(150, 143, 126), width=2)
            d.line((x0, y0 + 150, x0 + 92, y0 + 150), fill=(150, 143, 126), width=3)
    im.save(path)
    print(path)


def tex_library(path):
    """图书馆真实外观（据官网航拍017+正面018）：银白竖向石材线条与蓝色玻璃
    竖向条带相间，中部大面积蓝玻璃幕墙带横向分层，四角白色墙柱。"""
    im = Image.new('RGB', (W, H), (232, 234, 236))
    d = ImageDraw.Draw(im)
    # 竖向节奏：银白石材柱 + 蓝玻璃条带（每个 tile 约 24m 宽，12m 高=2层）
    # 背景先铺满蓝色玻璃
    d.rectangle((0, 0, W, H), fill=(72, 108, 140))
    for gy in range(0, H, 8):
        shade = int(96 + 26 * (0.5 + 0.5 * (gy % 64) / 64))
        d.line((0, gy, W, gy), fill=(shade - 8, shade + 20, shade + 42), width=1)
    # 竖向玻璃分格
    for gx in range(0, W, 42):
        d.line((gx, 0, gx, H), fill=(48, 76, 104), width=3)
    # 层间横梁
    for fl in range(2):
        y0 = fl * 256
        d.rectangle((0, y0 + 248, W, y0 + 256), fill=(210, 214, 218))
    # 白色竖向石材线条（宽条），间隔分布：每 128px 一根
    for bx in range(0, W, 128):
        # 主白柱，宽 24px，贯穿全高，中间有细窗
        d.rectangle((bx + 6, 0, bx + 34, H), fill=(236, 238, 240))
        d.line((bx + 6, 0, bx + 6, H), fill=(206, 210, 214), width=2)
        d.line((bx + 34, 0, bx + 34, H), fill=(206, 210, 214), width=2)
        # 白柱上的细长窗
        for fl in range(2):
            y0 = fl * 256
            d.rectangle((bx + 12, y0 + 40, bx + 28, y0 + 210), fill=(86, 120, 150))
            for wy in range(y0 + 46, y0 + 210, 16):
                d.line((bx + 12, wy, bx + 28, wy), fill=(64, 96, 126), width=1)
    # 玻璃反光斜带
    d.polygon([(40, H), (150, 0), (205, 0), (95, H)], fill=(120, 158, 188))
    im.save(path)
    print(path)


def tex_canteen(path):
    """食堂：浅色墙 + 大面积玻璃 + 横向雨棚"""
    im = Image.new('RGB', (W, H), (218, 216, 208))
    d = ImageDraw.Draw(im)
    for fl in range(2):
        y0 = fl * 256
        d.rectangle((0, y0 + 248, W, y0 + 256), fill=(180, 178, 170))
        for bay in range(3):
            x0 = 12 + bay * 170
            d.rectangle((x0, y0 + 36, x0 + 150, y0 + 208), fill=(66, 86, 104))
            d.rectangle((x0 + 3, y0 + 39, x0 + 147, y0 + 205), fill=(100, 136, 162))
            for gx in range(x0 + 3, x0 + 148, 30):
                d.line((gx, y0 + 39, gx, y0 + 205), fill=(60, 78, 96), width=2)
            d.rectangle((x0 - 4, y0 + 210, x0 + 154, y0 + 220), fill=(196, 194, 186))
    im.save(path)
    print(path)


def tex_roof_red(path):
    """宿舍坡屋顶/红色屋面瓦"""
    im = Image.new('RGB', (256, 256), (138, 66, 56))
    d = ImageDraw.Draw(im)
    for y in range(0, 256, 16):
        d.line((0, y, 256, y), fill=(110, 50, 44), width=2)
        for x in range((y // 16 % 2) * 8, 256, 16):
            d.line((x, y, x, y + 16), fill=(118, 54, 47), width=1)
    im.save(path)
    print(path)


tex_classroom(os.path.join(OUT, 'facade_classroom.jpg'))
tex_office(os.path.join(OUT, 'facade_office.jpg'))
tex_dorm(os.path.join(OUT, 'facade_dorm.jpg'))
tex_library(os.path.join(OUT, 'facade_library.jpg'))
tex_canteen(os.path.join(OUT, 'facade_canteen.jpg'))
tex_roof_red(os.path.join(OUT, 'roof_red.jpg'))
# 统一增强所有立面纹理的对比度与饱和度，让远景也能看清窗户
from PIL import ImageEnhance
import glob
for f in glob.glob(os.path.join(OUT, '*.jpg')):
    im = Image.open(f).convert('RGB')
    im = ImageEnhance.Contrast(im).enhance(1.25)
    im = ImageEnhance.Color(im).enhance(1.15)
    im.save(f, quality=92)
print('DONE', OUT)
