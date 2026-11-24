# -*- coding: utf-8 -*-
"""Fetch Gaode (Amap) satellite tiles and assemble a georeferenced campus image.

The output has EXACTLY the same pixel<->world mapping as the existing
satellite_z16/z17.jpg used by build_campus_v6.py:

    RESz  = 156543.03392 * cos(LAT0) / 2**z
    CX,CY = 1264/2, 625/2
    world pixel of (LAT0,LON0) at zoom z = (wx0, wy0)
    image top-left world pixel = (wx0-CX, wy0-CY)

So replacing the old file keeps every building polygon aligned.
"""
import math, os, io, urllib.request, time
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))

LAT0, LON0 = 34.7826, 113.8200
W, H = 1264, 625
CX, CY = W / 2, H / 2
TILE = 256
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Referer': 'https://www.amap.com/'}
HOSTS = ['webst01.is.autonavi.com', 'webst02.is.autonavi.com',
         'webst03.is.autonavi.com', 'webst04.is.autonavi.com']

def world_pixel(lat, lon, z):
    n = 256.0 * (2 ** z)
    wx = (lon + 180.0) / 360.0 * n
    s = math.sin(math.radians(lat))
    wy = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return wx, wy

def fetch_tile(x, y, z, retry=3):
    url = 'https://%s/appmaptile?style=6&x=%d&y=%d&z=%d' % (
        HOSTS[(x + y) % len(HOSTS)], x, y, z)
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=20).read()
            return Image.open(io.BytesIO(data)).convert('RGB')
        except Exception as e:
            if i == retry - 1:
                print('  tile fail', z, x, y, str(e)[:60])
                return Image.new('RGB', (TILE, TILE), (0, 0, 0))
            time.sleep(0.4)

def build(z, dst):
    wx0, wy0 = world_pixel(LAT0, LON0, z)
    left, top = wx0 - CX, wy0 - CY
    x0, y0 = int(math.floor(left / TILE)), int(math.floor(top / TILE))
    x1 = int(math.floor((left + W - 1) / TILE))
    y1 = int(math.floor((top + H - 1) / TILE))
    canvas = Image.new('RGB', ((x1 - x0 + 1) * TILE, (y1 - y0 + 1) * TILE))
    print('zoom', z, 'tiles', x0, x1, y0, y1, 'canvas', canvas.size)
    for ty in range(y0, y1 + 1):
        for tx in range(x0, x1 + 1):
            t = fetch_tile(tx, ty, z)
            canvas.paste(t, ((tx - x0) * TILE, (ty - y0) * TILE))
    ox, oy = int(round(left - x0 * TILE)), int(round(top - y0 * TILE))
    crop = canvas.crop((ox, oy, ox + W, oy + H))
    # sharpen slightly: Gaode imagery is softer than the old Tencent capture
    from PIL import ImageEnhance, ImageFilter
    crop = crop.filter(ImageFilter.UnsharpMask(radius=1.1, percent=110, threshold=3))
    crop = ImageEnhance.Contrast(crop).enhance(1.06)
    crop.save(dst, quality=92)
    print('SAVED', dst, crop.size)
    return dst

if __name__ == '__main__':
    build(16, os.path.join(OUT, 'satellite_gaode_z16.jpg'))
    build(17, os.path.join(OUT, 'satellite_gaode_z17.jpg'))
