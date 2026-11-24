# -*- coding: utf-8 -*-
"""Download WeChat article photos (jpg/png only) and build contact sheets."""
import json, os, io, urllib.request
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(ROOT, '..', 'output', 'ref_photos', 'wechat'))
IMGS = os.path.join(BASE, 'imgs')
os.makedirs(IMGS, exist_ok=True)

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Referer': 'https://mp.weixin.qq.com/'}

def sheet(prefix):
    files = sorted([f for f in os.listdir(IMGS) if f.startswith(prefix) and f.lower().endswith(('.jpg','.png'))],
                   key=lambda x: int(x.split('_')[2].split('.')[0]))
    if not files: return
    tw, th = 240, 180
    cols = 5
    rows = (len(files) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * tw, rows * (th + 22)), 'white')
    d = ImageDraw.Draw(canvas)
    for i, f in enumerate(files):
        try:
            im = Image.open(os.path.join(IMGS, f)).convert('RGB')
            im.thumbnail((tw - 6, th - 6))
            x = (i % cols) * tw + 3
            y = (i // cols) * (th + 22) + 3
            canvas.paste(im, (x, y))
            d.text((x + 3, y + th + 2), f, fill='black')
        except Exception as e:
            print('sheet err', f, e)
    out = os.path.join(BASE, 'sheet_' + prefix + '.jpg')
    canvas.save(out, quality=88)
    print('SHEET', out, canvas.size, len(files))

for tag in ['article_buildings', 'article_scenery']:
    urls = json.load(open(os.path.join(BASE, tag + '_urls.json'), encoding='utf-8'))
    n = 0
    for i, u in enumerate(urls):
        if 'qpic.cn' not in u or 'gif' in u.lower(): continue
        if '/0?wx_fmt' in u: continue
        ext = 'jpg' if ('jpeg' in u or 'jpg' in u) else 'png'
        fn = '%s_%03d.%s' % (tag, i, ext)
        path = os.path.join(IMGS, fn)
        if os.path.exists(path): n += 1; continue
        try:
            req = urllib.request.Request(u, headers=UA)
            data = urllib.request.urlopen(req, timeout=25).read()
            im = Image.open(io.BytesIO(data)).convert('RGB')
            if im.width < 200 or im.height < 150: continue
            im.save(path, quality=90)
            n += 1
        except Exception as e:
            print('FAIL', fn, str(e)[:80])
    print(tag, 'saved', n)
    sheet(tag)
