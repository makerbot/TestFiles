module die(radius, width, indent_radius, indent_depth){
	difference(){
		intersection(){
			sphere(radius);
			cube(2 * width, center=true);
		}
		translate([width, 0, 0]) scale([indent_depth/indent_radius, 1, 1])
			cube(indent_radius, center=true);
		translate([-width, 0, 0]) scale([indent_depth/indent_radius, 1, 1])
			cube(indent_radius, center=true);
		translate([0, width, 0]) scale([1, indent_depth/indent_radius, 1])
			cube(indent_radius, center=true);
		translate([0, -width, 0]) scale([1, indent_depth/indent_radius, 1])
			cube(indent_radius, center=true);
		translate([0, 0, width]) scale([1, 1, indent_depth/indent_radius])
			cube(indent_radius, center=true);
		translate([0, 0, -width]) scale([1, 1, indent_depth/indent_radius])
			cube(indent_radius, center=true);
	}
}

radius = 30;
width = 22;
indent_radius = 13;
indent_depth = 100;

die(radius, width, indent_radius, indent_depth);
