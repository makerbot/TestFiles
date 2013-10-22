module rounded_control(base, height, length, radius){
	hull(){
		cylinder(length, radius, radius);
		translate([base, 0, 0])
			cylinder(length, radius, radius);
		translate([0, height, 0])
			cylinder(length, radius, radius);
	}
}

module frame(base, height, length, radius, thickness){
	union(){
		difference(){
			translate([radius, radius, 0])
				rounded_control(base, height, length, radius);
			translate([thickness, thickness, -.5 * length])
				translate([radius-thickness, radius-thickness, 0])
					rounded_control(base, height, 2*length, radius-thickness);
		}
	}
}

module abacus(bar_length, bar_radius, num_pieces, piece_radius, piece_thickness, spacing){
	cylinder(bar_length, bar_radius, bar_radius, $fn=5);
	for (i=[1:num_pieces]){	
		translate([-.5*spacing, 0, i*(piece_thickness+spacing)])
			difference(){	
				cylinder(piece_thickness, piece_radius, piece_radius);
				cylinder(piece_thickness, bar_radius + spacing, bar_radius + spacing);
				translate([-3 * piece_radius + .5*spacing, -piece_radius, 0])
					cube([2 * piece_radius, 2 * piece_radius, piece_thickness]);
			}
	}
	
}


base = 45;
height = 60;
length = 14;
radius = 7.5;
thickness = 3;



bar_length = 60;
bar_radius = 2.5;
num_pieces = 4;
piece_radius = 7;
piece_thickness = 5;
spacing = 1;

union(){
	frame(base, height, length, radius, thickness);
	intersection(){
		translate([.5 * base, 0, .5*length])
			rotate([-90, -90, 0])
				abacus(bar_length, bar_radius, num_pieces, piece_radius, piece_thickness, spacing);
		translate([radius, radius, 0])
			rounded_control(base, height, length, radius);
	}
}