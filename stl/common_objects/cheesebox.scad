fn=50;
module array(xyc, xys, r, h){
	for(y = [0:xyc[1]-1]){
		if(y%2==0){
			for(x = [0:xyc[0]]){
				translate([x*xys[0],y*xys[1],0])
				cylinder(r=r,h=h,$fn=fn);
			}
		} else {
			for(x = [0:xyc[0]-1]){
				translate([(x+0.5)*xys[0],y*xys[1],0])
				cylinder(r=r,h=h,$fn=fn);
			}
		}
	}
}

module wall(xyz){
	difference(){
		cube(xyz);
		translate([25/2,25/2,0])
		array([xyz[0]/25-0.5,xyz[1]/20-0.25],[25,20],9,xyz[2]);
	}
}

wallxyz=[125,105,2];

translate([-wallxyz[0]/2,-wallxyz[0]/2,0])
rotate([90,0,0])
union(){
	translate([0,0,-wallxyz[0]+1*wallxyz[2]])
	cube([wallxyz[0],wallxyz[2],wallxyz[0]]);
	wall(wallxyz);
	translate([0,0,wallxyz[2]]){
		rotate([0,90,0]){
			wall(wallxyz);
			translate([0,0,wallxyz[0]-wallxyz[2]])
			wall(wallxyz);
		}
	}
	translate([0,0,-wallxyz[0]+wallxyz[2]])
	wall(wallxyz);
}