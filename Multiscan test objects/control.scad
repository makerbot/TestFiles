module control (base, height, length){
	linear_extrude(height=length)
		polygon([[0,0],[0,height],[base,0]]);
}

/*
base = 30;
height = 50;
length = 10;
control(base, height, length);
*/

module rounded_control(base, height, length, radius){
	hull(){
		cylinder(length, radius, radius);
		translate([base, 0, 0])
			cylinder(length, radius, radius);
		translate([0, height, 0])
			cylinder(length, radius, radius);
	}
}

base = 30;
height = 45;
length = 20;
radius = 3;
rounded_control(base, height, length, radius);

