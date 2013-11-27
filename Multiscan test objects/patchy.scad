module patchy(radius, length, thickness){
	difference(){
		rotate([0, 90, 0])
			cylinder(length, radius, radius, center=true);
		translate([-.5*(length - 2*thickness), thickness, thickness])
			cube([length - 2*thickness, radius, radius]);
		translate([-length, -radius, 0])
			cube([2*length, radius, radius]);
		translate([-length, -radius, -(radius+10)])
			cube([2*length, 2*radius, radius+10]);
	}
}

radius = 20;
length = 40;
thickness = 3;

patchy(radius, length, thickness);