include <Write.scad>
$fn=50;

module crosshairs(height, radius, thickness){
	difference(){
		union(){
			translate([-radius, -.5*thickness, height-1])
				cube([2*radius, thickness, height]);
			translate([-.5*thickness, -radius, height-1])
				cube([thickness, 2*radius, height]);
		}
		translate([0, 0, radius-1]) 
			cube(2*(radius-1), center=true);
	}
}

module write_radius(height, radius, thickness){
	translate([-.5*len(str(radius))*.5*height, -.5*height, height-1])
		write(str(radius), t=height, h=5);
}

module make_cylinder(height, radius){
	thickness = .5;

	difference(){
		cylinder(height, radius, radius);
		crosshairs(height, radius, thickness);
		if (radius >= 5)
			write_radius(height, radius, thickness);
	}
}

height = 5;
radius = 5;
make_cylinder(height, radius);
