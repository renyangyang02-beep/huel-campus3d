#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用设备码授权拿到的 token 创建 GitHub 仓库并推送本地提交。"""
import json, os, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE = os.path.join(ROOT, 'output', '_gh_token.txt')
REPO_NAME = 'huel-campus3d'
PROXY = 'http://127.0.0.1:7897'


def api(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Authorization', 'Bearer ' + TOKEN)
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data:
        req.add_header('Content-Type', 'application/json')
    proxy = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    op = urllib.request.build_opener(proxy)
    with op.open(req, timeout=30) as r:
        return json.loads(r.read().decode())


def run(cmd, env=None):
    e = os.environ.copy()
    e['HTTPS_PROXY'] = PROXY
    e['HTTP_PROXY'] = PROXY
    e['https_proxy'] = PROXY
    e['http_proxy'] = PROXY
    if env:
        e.update(env)
    print('$', ' '.join(cmd[:3]) + (' ...' if len(cmd) > 3 else ''), flush=True)
    r = subprocess.run(cmd, cwd=ROOT, env=e, capture_output=True, text=True)
    if r.returncode != 0:
        print('STDOUT:', r.stdout[-2000:], flush=True)
        print('STDERR:', r.stderr[-2000:], flush=True)
        raise SystemExit('命令失败: ' + cmd[0])
    if r.stdout.strip():
        print(r.stdout.strip()[-1500:], flush=True)
    return r.stdout


if not os.path.exists(TOKEN_FILE):
    raise SystemExit('未找到授权令牌，请确认网页授权已完成。')
TOKEN = open(TOKEN_FILE, encoding='utf-8').read().strip()

print('=== 1. 确认 GitHub 账号 ===', flush=True)
me = api('GET', 'https://api.github.com/user')
owner = me['login']
print('账号:', owner, '| 名称:', me.get('name'), flush=True)

print('=== 2. 创建仓库（已存在则复用）===', flush=True)
try:
    repo = api('GET', 'https://api.github.com/repos/%s/%s' % (owner, REPO_NAME))
    print('仓库已存在:', repo['html_url'], flush=True)
except urllib.error.HTTPError as e:
    if e.code != 404:
        raise
    repo = api('POST', 'https://api.github.com/user/repos', {
        'name': REPO_NAME,
        'description': '河南财经政法大学郑东校区 3D 实景导览（61 栋建筑 / Three.js / Blender）',
        'private': False,
        'has_issues': True,
        'has_wiki': False,
    })
    print('仓库已创建:', repo['html_url'], flush=True)

print('=== 3. 配置远程并推送 ===', flush=True)
url = 'https://x-access-token:%s@github.com/%s/%s.git' % (TOKEN, owner, REPO_NAME)
# 移除旧 remote（若有）
run(['git', 'remote', 'remove', 'origin']) if subprocess.run(
    ['git', 'remote', 'get-url', 'origin'], cwd=ROOT, capture_output=True
).returncode == 0 else None
run(['git', 'remote', 'add', 'origin', url])
# 确保分支名为 main
run(['git', 'branch', '-M', 'main'])
run(['git', 'push', '-u', 'origin', 'main'])

print('=== 4. 验证远端 ===', flush=True)
run(['git', 'ls-remote', '--heads', 'origin'])
print('\n完成！仓库地址: https://github.com/%s/%s' % (owner, REPO_NAME), flush=True)
