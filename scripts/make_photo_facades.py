# -*- coding: utf-8 -*-
"""Photo-based library facade texture from a clean, unobstructed wall patch.

The front photo of the library (article_scenery_008.jpg) has a large central
band of silver stone piers + blue glass with no trees/sky. We crop two floors
of it and mirror-tile to make a seamless texture. Other buildings keep the
procedural textures in make_facades.py (photo crops of them had perspective
and foliage, so were rejected).
"""
from PIL import Image, ImageEnhance, ImageFilter
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.abspath(os.path.join(ROOT, '..', 'output', 'ref_photos', 'wechat', 'imgs'))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output', 'tex'))
os.makedirs(OUT, exist_ok=True)

im = Image.open(os.path.join(IMG, 'article_scenery_008.jpg')).convert('RGB')
# central 2-floor band: silver piers + blue glass, no trees, no sky, no entrance
crop = im.crop((320, 330, 620, 500))
w, h = crop.size
canvas = Image.new('RGB', (w * 2, h * 2))
canvas.paste(crop, (0, 0))
canvas.paste(crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (w, 0))
canvas.paste(crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (0, h))
canvas.paste(crop.transpose(Image.Transpose.ROTATE_180), (w, h))
tile = canvas.crop((w // 2, h // 2, w // 2 + w, h // 2 + h)).resize((512, 512), Image.LANCZOS)
tile = ImageEnhance.Contrast(tile).enhance(1.10)
tile = tile.filter(ImageFilter.UnsharpMask(1.0, 70, 3))
path = os.path.join(OUT, 'facade_library_photo.jpg')
tile.save(path, quality=93)
print('SAVED', path)
