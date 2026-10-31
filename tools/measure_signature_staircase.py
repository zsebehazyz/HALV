#!/usr/bin/env python3
"""Measure visible stair horizontals in the left-stem ROI, without interpreting them."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def main():
    name='research/sources/cryptoHALV.png';p=np.array(Image.open(ROOT/name))
    x0,y0,x1,y1=788,830,868,930
    assert set(np.unique(p[y0:y1,x0:x1]))=={0,255}
    rows=[]
    for y in range(y0,y1):
        edges=np.flatnonzero(np.diff(np.r_[False,p[y,x0:x1]==255,False]))
        for start,end in zip(edges[::2],edges[1::2]):
            if end-start>=4:rows.append({'y':y,'x_start':x0+int(start),'x_end_inclusive':x0+int(end)-1,'width':int(end-start)})
    groups=[]
    for row in rows:
        if (groups and row['y']==groups[-1]['y_end_inclusive']+1
            and row['x_start']==groups[-1]['x_start'] and row['x_end_inclusive']==groups[-1]['x_end_inclusive']):
            groups[-1]['y_end_inclusive']=row['y']
        else:groups.append({**{k:v for k,v in row.items() if k!='y'},'y_start':row['y'],'y_end_inclusive':row['y']})
    for g in groups:
        g['center_y']=(g['y_start']+g['y_end_inclusive'])/2
        g['touches_right_roi_boundary']=g['x_end_inclusive']==x1-1
    out={'source':name,'source_sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'roi_xyxy_exclusive':[x0,y0,x1,y1],'predicate':'white horizontal run >=4 pixels; adjacent identical rows merged',
         'horizontals':groups,
         'left_endpoint_spacings_px':[b['x_start']-a['x_start'] for a,b in zip(groups,groups[1:])],
         'center_y_spacings_px':[b['center_y']-a['center_y'] for a,b in zip(groups,groups[1:])],
         'limitations':['Last run is clipped by the ROI; continuation overlaps label region',
                        'Five visible runs are not evidence for exactly five encoded data blocks',
                        'No exact halving rule or numeric normalization follows from these row spacings alone'],
         'no_private_key_search':True}
    (ROOT/'research/data/signature_staircase_geometry.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
