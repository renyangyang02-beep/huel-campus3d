# 云上财大 · 河南财经政法大学（郑东校区）三维实景导览

基于官方平面图配准 + 实景照片复原的校园 3D 导览，可在浏览器旋转、缩放、点击建筑查看信息，并提供实景照片、矢量刻度小地图与室内空间示意。

## 功能

- 三维校园：61 栋建筑，含图书馆、教学楼、建树楼、大学生科创中心（鼎新楼双塔）、笃行书院、新苑、商业街、教职工活动中心、体育训练馆及东南西北四门
- 点位速览：点击左侧图标快速飞到对应建筑
- 实景照片：照片分类按楼体题字逐张核实，见 [实景相册](web/gallery.html)
- 矢量刻度小地图：100m 网格 + 建筑轮廓 + 动态比例尺，放大不模糊
- 室内示意：部分建筑可进入查看内部空间

## 目录结构

```
.
├── web/                  网页资源（index.html 主入口、gallery.html 相册）
│   ├── vendor/           three.js 等第三方库
│   ├── realphotos/       实景照片
│   └── buildings.json    建筑数据（含轮廓点、坐标、楼层）
├── output/               建模产物
│   ├── campus_exterior.glb   室外三维模型
│   ├── campus_interiors.glb  室内三维模型
│   ├── HUEL_Zhengdong_Campus.blend  Blender 源文件
│   └── buildings_v18.json    建模数据源（世界坐标轮廓）
├── scripts/              Blender 建模与数据处理脚本
└── publish/              发布副本（与 web/ + output/ 关键文件一致）
```

## 本地运行

直接双击 HTML 无法加载模型（相对路径失效），需通过 HTTP 服务访问：

```bash
# 在项目根目录执行
python -m http.server 8123
# 浏览器打开 http://127.0.0.1:8123/web/index.html
```

## 重新建模

需要 Blender 的 Python 环境（bpy）：

```bash
python scripts/make_v18_data.py      # 生成建筑数据
python scripts/build_campus_v18.py   # 生成 GLB 模型
python scripts/sync_web_pts.py v18   # 同步轮廓点到网页数据
```

## 技术栈

Blender (bpy) 建模 → GLB/glTF 导出 → Three.js + GLTFLoader 渲染；纯静态站点，无后端依赖。

## 说明

建筑高度为常见层数示意，非测绘成果；建筑位置与轮廓依据学校官方平面图矢量化。实景照片来自学校官网与公开渠道，仅作校园展示用途。
