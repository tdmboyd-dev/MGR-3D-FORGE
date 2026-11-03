from pathlib import Path
import json
from tests.test_multiview import mask_png
from forge.multiview import export_reconstruction, score_against_solid

root=Path('evidence/image3d-core-2026-11-02/calibrated-profile-final')
root.mkdir()
size=32
# An original stepped vessel profile with changing width/depth at measured heights.
# Every horizontal slice is a rectangle, so its two orthographic silhouettes
# uniquely constrain this fixture at the voxel grid (not arbitrary objects).
bands=[(0,4,8,24,8,24),(4,18,4,28,6,26),(18,24,10,22,10,22),(24,32,6,26,7,25)]
for axis in ('front','left'):
    rows=[]
    for image_y in range(size):
        y=size-1-image_y
        band=next(item for item in bands if item[0]<=y<item[1])
        low,high=band[2:4] if axis=='front' else band[4:6]
        rows.append([low<=x<high for x in range(size)])
    (root/(axis+'.png')).write_bytes(mask_png(rows))
spec={'grid':size,'bounds':{'width':2.,'height':3.,'depth':2.},
      'views':[{'axis':axis,'mask':axis+'.png'} for axis in ('front','left')]}
path=root/'spec.json'
path.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
result=export_reconstruction(path,root/'hull',marching=True)
boxes=[{'min':[-1+xl*2/size,yl*3/size,-1+zl*2/size],
        'max':[-1+xh*2/size,yh*3/size,-1+zh*2/size]}
       for yl,yh,xl,xh,zl,zh in bands]
scored=score_against_solid({**spec,'base_dir':str(root)},boxes)
(root/'analytic-ground-truth.json').write_text(json.dumps({'fixture_kind':'owner-authored analytic union of boxes',
       'boxes':boxes,'score':scored},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'triangles':result['manifest']['triangles'],
                   'voxel_vs_analytic_iou':scored['hull_vs_solid_iou']}))
