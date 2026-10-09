"""Parametric rectangular enclosure. Exact surface mesh; no voxel approximation.

Meshes are assembled on a common coordinate grid, then interior faces removed.
All STL triangles are oriented outwards. Dimensions are millimetres.
"""
from pathlib import Path
from collections import Counter
import itertools
import struct

OUT = Path(__file__).parent
W, H, D, T = 150, 100, 55, 2.4

def rect(x, y, z, w, h, d):
    return (x, y, z, x+w, y+h, z+d)

def inside(box, p):
    return all(box[i] < p[i] < box[i+3] for i in range(3))

def mesh(name, positive, negative):
    grid = [sorted({b[i] for b in positive+negative} | {b[i+3] for b in positive+negative}) for i in range(3)]
    cells = set()
    for ijk in itertools.product(*(range(len(g)-1) for g in grid)):
        p = tuple((grid[i][k]+grid[i][k+1])/2 for i,k in enumerate(ijk))
        if any(inside(b,p) for b in positive) and not any(inside(b,p) for b in negative): cells.add(ijk)
    tris = []
    # Corners ordered so each face's normal points away from the material.
    faces = [((-1,0,0),[(0,0,0),(0,0,1),(0,1,1),(0,1,0)]),
             ((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),
             ((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),
             ((0,1,0),[(0,1,0),(0,1,1),(1,1,1),(1,1,0)]),
             ((0,0,-1),[(0,0,0),(0,1,0),(1,1,0),(1,0,0)]),
             ((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)])]
    for ijk in cells:
        for n,corners in faces:
            if tuple(a+b for a,b in zip(ijk,n)) in cells: continue
            v=[tuple(grid[i][ijk[i]+c[i]] for i in range(3)) for c in corners]
            tris.extend([(n,v[0],v[1],v[2]),(n,v[0],v[2],v[3])])
    edges=Counter()
    for _,a,b,c in tris:
        for u,v in [(a,b),(b,c),(c,a)]:edges[tuple(sorted((u,v)))]+=1
    assert all(v==2 for v in edges.values()), name+' is not manifold'
    with (OUT/(name+'.stl')).open('wb') as f:
        f.write(('Lymyt fit prototype / mm / '+name).encode().ljust(80,b' '));f.write(struct.pack('<I',len(tris)))
        for n,a,b,c in tris:f.write(struct.pack('<12fH',*(n+a+b+c),0))
    print(name, len(tris), 'triangles; every edge shared by 2 faces')

def build():
    posts=[(T,T),(W-T-12,T),(T,H-T-12),(W-T-12,H-T-12)]
    positives=[rect(0,0,0,W,H,D)]
    # Build hollow body and posts as union; hollowing must not cut posts away.
    shell=[rect(0,0,0,W,H,T),rect(0,0,T,T,H,D-T),rect(W-T,0,T,T,H,D-T),rect(T,0,T,W-2*T,T,D-T),rect(T,H-T,T,W-2*T,T,D-T)]
    shell += [rect(x,y,D-12,12,12,12) for x,y in posts]
    holes=[rect(32,44,-1,34,34,T+2),rect(84,44,-1,34,34,T+2),rect(72,55,-1,6,6,T+2),rect(70,22,-1,10,10,T+2),rect(-1,20,12,T+2,20,14)]
    for x,y in posts:
        holes += [rect(x+4.3,y+4.3,D-13,3.4,3.4,15),rect(x+3.1,y+3.1,D-13,5.8,5.8,4)]
    mesh('lymyt-body',shell,holes)
    lidholes=[rect(x+4.3,y+4.3,-1,3.4,3.4,T+2) for x,y in posts]
    mesh('lymyt-back',[rect(0,0,0,W,H,T)],lidholes)
    # Small first print: eye frame and samples of clearance, before the full body.
    mesh('lymyt-fit-test',[rect(0,0,0,44,44,T),rect(44,0,0,16,44,T)],
         [rect(5,5,-1,34,34,T+2),rect(48,6,-1,6,6,T+2),rect(47,22,-1,10,10,T+2)])
    scad='''// Lymyt v0.2 — FIT PROTOTYPE, not a measured production enclosure.
// Millimetres. part: body, back, fit-test. Preview/measure before printing.
part = "body";
width=150; height=100; depth=55; wall=2.4;
eye=34; eye_y=44; left_x=32; right_x=84;
button_x=70; button_y=22; button_size=10;
usb_y=20; usb_z=12; usb_width=20; usb_height=14;
module box(x,y,z,w,h,d){translate([x,y,z])cube([w,h,d]);}
module holes(){
 for(x=[left_x,right_x]) box(x,eye_y,-1,eye,eye,wall+2);
 box(72,55,-1,6,6,wall+2);
 box(button_x,button_y,-1,button_size,button_size,wall+2);
 box(-1,usb_y,usb_z,wall+2,usb_width,usb_height);
}
module posts(){for(x=[wall,width-wall-12])for(y=[wall,height-wall-12])box(x,y,depth-12,12,12,12);}
module bolt_holes(lid=false){for(x=[wall,width-wall-12])for(y=[wall,height-wall-12]){
 box(x+4.3,y+4.3,lid?-1:depth-13,3.4,3.4,lid?wall+2:15);
 if(!lid)box(x+3.1,y+3.1,depth-13,5.8,5.8,4);
}}
module body(){difference(){union(){difference(){cube([width,height,depth]);box(wall,wall,wall,width-2*wall,height-2*wall,depth);}posts();}holes();bolt_holes();}}
module back(){difference(){cube([width,height,wall]);bolt_holes(true);}}
module test(){difference(){cube([60,44,wall]);box(5,5,-1,eye,eye,wall+2);box(48,6,-1,6,6,wall+2);box(47,22,-1,10,10,wall+2);}}
if(part=="body")body();else if(part=="back")back();else if(part=="fit-test")test();
'''
    (OUT/'lymyt.scad').write_text(scad)

if __name__ == '__main__':build()
