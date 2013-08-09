//SPUUUUUUURS
$fn = 50;

spurWidth = .3;

r1 = 30;
r2 = 25;
r3 = 15;

height = 15;

module tube(height, radius){
	difference(){
		cylinder(height, radius, radius);
		scale([1,1,2]) cylinder(height, radius-spurWidth, radius-spurWidth, center=true);
	}
}

tube(height, r1);
difference(){
	tube(height, r2);
	translate([0,r2,0]) cube(2*height, center=true);
}
union(){
	difference(){
		translate([0,0,.5*height]) cube([2*r3, 2*r3, height], center=true);
		translate([0,spurWidth,.5*height]) cube([2*r3-2*spurWidth, 2*r3, 2*height], center=true);
	}
	translate([-r3, -.5*spurWidth, 0]) cube([2*r3+.5*(r2-r3), spurWidth, height]);
	translate([0,0,.5*height]) cube([spurWidth, 2*r3, height], center=true);

}