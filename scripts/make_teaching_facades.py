# -*- coding: utf-8 -*-
"""v12: draw clean, tileable teaching-building facades from real-photo features.
Style A (axis)  : first/second teaching hall — light grey vertical fins + blue glass bands
Style B (gray)  : teaching.jpg — dark grey brick + blue glass curtain + reddish bands
Each texture = 2 floors tall (512x512), used with v_repeat = floors/2.
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import os, random

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output', 'tex'))
W = H = 512
FLOOR = H // 2  # 256 px per floor
random.seed(12)


def style_axis():
    """中轴第一/第二教学楼：浅灰竖向格栅 + 蓝玻璃窗带（据 axis_front.jpg）"""
    im = Image.new('RGB', (W, H), (206, 207, 203))
    d = ImageDraw.Draw(im)
    for fl in range(2):
        y0 = fl * FLOOR
        # 楼层分隔带（浅灰混凝土）
        d.rectangle((0, y0, W, y0 + 14), fill=(188, 189, 185))
        d.line((0, y0 + 13, W, y0 + 13), fill=(166, 168, 164), width=2)
        # 窗台带
        d.rectangle((0, y0 + 232, W, y0 + 244), fill=(196, 197, 193))
        # 一排窗：蓝灰玻璃，白框
        for bay in range(6):
            bx = 8 + bay * 85
            # 窗洞
            d.rectangle((bx, y0 + 30, bx + 74, y0 + 218), fill=(236, 236, 232))
            d.rectangle((bx + 4, y0 + 34, bx + 70, y0 + 214), fill=(92, 122, 146))
            # 玻璃反光渐变（上亮下暗）
            for yy in range(y0 + 34, y0 + 214, 6):
                t = (yy - (y0 + 34)) / 180.0
                c = (int(120 - 40 * t), int(150 - 40 * t), int(172 - 35 * t))
                d.line((bx + 4, yy, bx + 70, yy), fill=c, width=6)
            # 竖向窗棂
            d.line((bx + 37, y0 + 34, bx + 37, y0 + 214), fill=(224, 226, 224), width=3)
            d.line((bx + 4, y0 + 124, bx + 70, y0 + 124), fill=(224, 226, 224), width=3)
        # 密集竖向格栅（财大教学楼标志：白/浅灰竖肋贯穿立面）
        for gx in range(0, W, 17):
            shade = (222, 223, 219) if (gx // 17) % 2 == 0 else (210, 211, 207)
            d.rectangle((gx, y0 + 14, gx + 4, y0 + 232), fill=shade)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = im.filter(ImageFilter.UnsharpMask(1, 60, 2))
    return im


def style_gray():
    """deep grey brick + blue glass curtain + reddish bands (teaching.jpg)"""
    im = Image.new('RGB', (W, H), (74, 76, 78))
    d = ImageDraw.Draw(im)
    # 深灰砖肌理
    for by in range(0, H, 10):
        d.line((0, by, W, by), fill=(64, 66, 68), width=1)
        off = 12 if (by // 10) % 2 else 0
        for bx in range(off, W, 24):
            d.line((bx, by, bx, by + 10), fill=(68, 70, 72), width=1)
    for fl in range(2):
        y0 = fl * FLOOR
        # 红褐色横向装饰带
        d.rectangle((0, y0 + 16, W, y0 + 26), fill=(146, 92, 80))
        d.line((0, y0 + 26, W, y0 + 26), fill=(118, 72, 62), width=2)
        # 四个开间
        for bay in range(4):
            bx = 14 + bay * 126
            # 蓝玻璃窗（白框）
            d.rectangle((bx, y0 + 46, bx + 112, y0 + 210), fill=(228, 228, 224))
            d.rectangle((bx + 5, y0 + 51, bx + 107, y0 + 205), fill=(46, 76, 106))
            for yy in range(y0 + 51, y0 + 205, 5):
                t = (yy - (y0 + 51)) / 154.0
                c = (int(74 - 34 * t), int(112 - 40 * t), int(142 - 36 * t))
                d.line((bx + 5, yy, bx + 107, yy), fill=c, width=5)
            # 竖窗棂
            for wx in (bx + 39, bx + 73):
                d.line((wx, y0 + 51, wx, y0 + 205), fill=(210, 212, 210), width=3)
            d.line((bx + 5, y0 + 128, bx + 107, y0 + 128), fill=(210, 212, 210), width=3)
            # 空调外机小方块（实景特征）
            for ac in (bx + 20, bx + 88):
                d.rectangle((ac, y0 + 214, ac + 16, y0 + 228), fill=(196, 196, 190))
                d.rectangle((ac + 2, y0 + 216, ac + 14, y0 + 226), fill=(168, 168, 162))
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = im.filter(ImageFilter.UnsharpMask(1, 70, 2))
    return im


a = style_axis()
b = style_gray()
a.save(os.path.join(OUT, 'facade_teach_axis.jpg'), quality=94)
b.save(os.path.join(OUT, 'facade_teach_gray.jpg'), quality=94)
# 预览拼接
prev = Image.new('RGB', (1024, 512), 'white')
prev.paste(a.resize((512, 512)), (0, 0))
prev.paste(b.resize((512, 512)), (512, 0))
prev.save(os.path.join(OUT, 'facade_teach_v12_preview.png'))
print('saved facade_teach_axis.jpg / facade_teach_gray.jpg')
