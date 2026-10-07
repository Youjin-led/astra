"""Проверки компоновки корпуса и раскроя; не расчёт прочности."""
import json, pathlib
from project_data import PARTS, PANELS
ROOT=pathlib.Path(__file__).resolve().parent
assert len({p['id'] for p in PARTS})==len(PARTS)
assert all(all(v>0 for v in p['size']) for p in PARTS)
def bounds(p):return [(c-s/2,c+s/2) for c,s in zip(p['pos'],p['size'])]
solid=[p for p in PARTS if p['stage']<=5]
for i,a in enumerate(solid):
    for b in solid[i+1:]:
        overlap=[min(aa[1],bb[1])-max(aa[0],bb[0]) for aa,bb in zip(bounds(a),bounds(b))]
        assert not all(v>1e-5 for v in overlap),(a['id'],b['id'],'intersect',overlap)
for p in PARTS:
    if p['stage']<=5:
        b=bounds(p)
        assert -600<=b[0][0]<=b[0][1]<=600 and 0<=b[2][0]<=b[2][1]<=800
panes=[p for p in PARTS if p['stage']==8]
for i,a in enumerate(panes):
    for b in panes[i+1:]:
        ba,bb=bounds(a),bounds(b)
        assert min(ba[0][1],bb[0][1])-max(ba[0][0],bb[0][0])<=0 or min(ba[2][1],bb[2][1])-max(ba[2][0],bb[2][0])<=0
    for d in [p for p in PARTS if p['stage']==7]:
        ba,bd=bounds(a),bounds(d)
        # A panel must have a clear straight removal path toward -Y.
        assert min(ba[0][1],bd[0][1])-max(ba[0][0],bd[0][0])<=0 or min(ba[2][1],bd[2][1])-max(ba[2][0],bd[2][0])<=0,(a['id'],d['id'],'blocks removal')
plan=json.loads((ROOT/'cut_plan.json').read_text())
expected={p['id']:max(p['size'][0],p['size'][2]) for p in PARTS if p['material']=='Фанера 15'}
actual={}
for strip in plan['strips']:
    assert sum(v for _,v in strip)+plan['kerf_mm']*(len(strip)-1)<=plan['stock_length_mm']
    for code,length in strip:
        assert code not in actual;actual[code]=length
assert actual==expected
assert len(plan['strips'])*(70+3)-3<=1220
assert len(panes)==5
print('PASS:',len(PARTS),'unique parts; cabinet nonintersection; five removable panels; strip cutting matches BOM.')
print('Not tested: concept relief clearances, joints/load capacity, wall anchors, actual exhibits and hardware.')
