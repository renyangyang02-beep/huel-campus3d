# -*- coding: utf-8 -*-
"""v12: derive build_campus_v12.py from v11 — real-photo teaching facades,
eaves + entrance canopy + window bands, correct heights/names."""
import io, os
ROOT=os.path.dirname(os.path.abspath(__file__))
s=io.open(os.path.join(ROOT,'build_campus_v11.py'),encoding='utf-8').read()

s=s.replace('v11: rebuild HUEL Zhengdong campus from OFFICIAL CAMPUS PLAN (authoritative layout)',
            'v12: plan-based campus + photo-faithful teaching buildings (fins/glass/eaves/canopy)')

# data source v11 -> v12
s=s.replace("buildings_v11.json","buildings_v12.json")

# 1) texture library: teaching facades
s=s.replace(
" 'classroom':texmat('fac_classroom',os.path.join(TEXDIR,'facade_classroom.jpg')),",
" 'classroom':texmat('fac_classroom_v12',os.path.join(TEXDIR,'facade_teach_axis.jpg')),")
s=s.replace(
"_lab_tex=os.path.join(TEXDIR,'facade_lab_red.jpg')\nT['lab']=texmat('fac_lab_red',_lab_tex) if os.path.exists(_lab_tex) else T['classroom']",
"_lab_tex=os.path.join(TEXDIR,'facade_teach_gray.jpg')\nT['lab']=texmat('fac_lab_gray',_lab_tex) if os.path.exists(_lab_tex) else T['classroom']\nT['teach_axis']=texmat('fac_teach_axis',os.path.join(TEXDIR,'facade_teach_axis.jpg'))\nT['teach_gray']=texmat('fac_teach_gray',os.path.join(TEXDIR,'facade_teach_gray.jpg'))")

# 2) per-building facade selection (before fmat use in build loop)
s=s.replace(
"    fmat=T.get(b['kind'],T['classroom'])\n    if 'inner' in b:",
"    fmat=T.get(b['kind'],T['classroom'])\n    if b.get('facade')=='axis': fmat=T['teach_axis']\n    elif b.get('facade')=='gray': fmat=T['teach_gray']\n    if 'inner' in b:")

# 3) Teaching buildings: add eave + glass band under eave + entrance canopy + fin lines
old="""        else:
            add_prism('B_%s_roof'%name,pts,1.6,M['roof'],build_col,z0=b['height']).parent=parent
        add_roof_details(name,pts,b,build_col,parent)
"""
new="""        else:
            add_prism('B_%s_roof'%name,pts,1.6,M['roof'],build_col,z0=b['height']).parent=parent
        # v12: 教学楼真实特征——大挑檐 + 檐下玻璃带 + 南向入口雨棚 + 立面竖鳍
        if b['kind'] in ('classroom','lab') or b.get('facade') in ('axis','gray'):
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            # 宽大挑檐（略外扩），如教学楼顶部出挑屋盖
            e=1.06
            eave=[(cx+(x-cx)*e, cy+(y-cy)*e) for x,y in pts]
            add_prism('B_%s_teave'%name,eave,2.2,M['trim'],build_col,z0=b['height']-0.6).parent=parent
            add_prism('B_%s_tglass'%name,pts,1.4,M['glass2'],build_col,z0=b['height']-2.4).parent=parent
            # 入口雨棚（朝南，位于轮廓最南边）
            ey=min(ys)
            add_box('B_%s_canopy'%name,(cx,ey-3.4,6.0),(bx*0.34,6.5,0.9),M['trim'],build_col,parent)
            for k in (-1,1):
                add_cyl('B_%s_col_%d'%(name,k),(cx+k*bx*0.14,ey-5.6,3.0),0.5,6,M['trim'],build_col,parent=parent)
        add_roof_details(name,pts,b,build_col,parent)
"""
assert old in s, 'roof branch not found'
s=s.replace(old,new,1)

# 4) meta note
s=s.replace('建筑位置、轮廓与名称依据学校官方《郑东校区平面图》矢量化复原（真实格局），地面采用该官方平面图；建筑高度按类型示意，非测绘成果。',
 '建筑位置、轮廓与名称依据学校官方《郑东校区平面图》矢量化复原（真实格局），地面采用该官方平面图；教学楼立面按实景重绘（浅灰竖格栅/深灰砖墙+蓝玻璃、挑檐与入口雨棚），高度为常见层数示意，非测绘成果。')

dst=os.path.join(ROOT,'build_campus_v12.py')
io.open(dst,'w',encoding='utf-8').write(s)
print('wrote',dst,len(s))
