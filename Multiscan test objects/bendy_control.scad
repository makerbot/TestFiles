module rounded_control(base, height, length, radius){
	hull(){
		cylinder(length, radius, radius);
		translate([base, 0, 0])
			cylinder(length, radius, radius);
		translate([0, height, 0])
			cylinder(length, radius, radius);
	}
}

module bendy_control(base, height, length, radius){
	union(){
		difference(){
			translate([radius, radius, 0])
				rounded_control(base, height, length, radius);
			translate([1, 1, -.5 * length])
				translate([radius-1, radius-1, 0])
					rounded_control(base, height, 2*length, radius-1);
		}
		translate([radius, radius, 0]){
			cylinder(length, radius, radius);
			translate([base, 0, 0])
				cylinder(length, radius, radius);
			translate([0, height, 0])
				cylinder(length, radius, radius);
		}
	}
}

base = 30 * 1.5;
height = 45 * 1.5;
length = 20 * 1.5;
radius = 5 * 1.5;
bendy_control(base, height, length, radius);
