// Lymyt v0.3 — LED-free — FIT PROTOTYPE, not a measured production enclosure.
// Millimetres. part: body, back, fit-test. Preview/measure before printing.
part = "body";
width=150; height=100; depth=55; wall=2.4;
eye=34; eye_y=44; left_x=32; right_x=84;
button_x=70; button_y=22; button_size=10;
usb_y=20; usb_z=12; usb_width=20; usb_height=14;
module box(x,y,z,w,h,d){translate([x,y,z])cube([w,h,d]);}
module holes(){
 for(x=[left_x,right_x]) box(x,eye_y,-1,eye,eye,wall+2);
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
module test(){difference(){cube([60,44,wall]);box(5,5,-1,eye,eye,wall+2);box(47,22,-1,10,10,wall+2);}}
if(part=="body")body();else if(part=="back")back();else if(part=="fit-test")test();
