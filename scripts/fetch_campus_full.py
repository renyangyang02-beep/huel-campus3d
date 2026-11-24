# -*- coding: utf-8 -*-
"""Fetch a HIGH-RESOLUTION satellite image covering the ENTIRE HUEL Zhengdong campus.
Previous z17 image (1264x625) only covered ~1.24km of the ~2.5km campus, so most
buildings were never modelled. This builds a z17-resolution mosaic covering the
full campus (~2.5km x 1.6km) using the same Gaode no-label tiles.

Coordinate contract (must match build_campus_v9.py):
  LAT0, LON0 = campus reference point
  W,H = full mosaic size
  CX,CY = W/2, H/2
  world pixel of (LAT0,LON0) at z = (wx0,wy0)
  image top-left world pixel = (wx0-CX, wy0-CY)
  => px_to_xy(px,py) = ((px-CX)*RES17, (CY-py)*RES17)
"""
import math, os, io, urllib.request, time
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))

LAT0, LON0 = 34.7826, 113.8200
Z = 17
# Full campus mosaic: cover enough to include dorms north/west/south + sports fields.
# 2.5km wide at RES17~0.98m/px -> ~2560px; use 2816x1664 (11x6.5 tiles) for margin.
W, H = 2816, 1792
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

def fetch_tile(x, y, z, retry=4):
    url = 'https://%s/appmaptile?style=6&x=%d&y=%d&z=%d' % (
        HOSTS[(x + y) % len(HOSTS)], x, y, z)
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=25).read()
            return Image.open(io.BytesIO(data)).convert('RGB')
        except Exception as e:
            if i == retry - 1:
                print('  tile fail', z, x, y, str(e)[:60], flush=True)
                return Image.new('RGB', (TILE, TILE), (0, 0, 0))
            time.sleep(0.5)

def build():
    wx0, wy0 = world_pixel(LAT0, LON0, Z)
    left, top = wx0 - CX, wy0 - CY
    x0, y0 = int(math.floor(left / TILE)), int(math.floor(top / TILE))
    x1 = int(math.floor((left + W - 1) / TILE))
    y1 = int(math.floor((top + H - 1) / TILE))
    canvas = Image.new('RGB', ((x1 - x0 + 1) * TILE, (y1 - y0 + 1) * TILE))
    total = (x1 - x0 + 1) * (y1 - y0 + 1)
    print('zoom', Z, 'tiles', total, 'grid', x0, x1, y0, y1, 'canvas', canvas.size, flush=True)
    k = 0
    for ty in range(y0, y1 + 1):
        for tx in range(x0, x1 + 1):
            t = fetch_tile(tx, ty, Z)
            canvas.paste(t, ((tx - x0) * TILE, (ty - y0) * TILE))
            k += 1
            if k % 10 == 0: print('  fetched', k, '/', total, flush=True)
    ox, oy = int(round(left - x0 * TILE)), int(round(top - y0 * TILE))
    crop = canvas.crop((ox, oy, ox + W, oy + H))
    crop = crop.filter(ImageFilter.UnsharpMask(radius=1.0, percent=100, threshold=3))
    crop = ImageEnhance.Contrast(crop).enhance(1.05)
    dst = os.path.join(OUT, 'satellite_full_z17.jpg')
    crop.save(dst, quality=93)
    print('SAVED', dst, crop.size, flush=True)
    return dst

if __name__ == '__main__':
    build()
