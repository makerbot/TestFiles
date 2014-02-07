include <Write.scad>

module anchors(width, depth, height, length){
	cube([width, depth, height]);
	translate([length+width, 0, 0])
		cube([width, depth, height]);
}

module bridge(width, depth, height, length, thickness){
	translate([0, 0, height-thickness])
		cube([length + 2*thickness, depth, thickness]);
}

module write_length(depth, length){
	translate([-(2 + 4*len(str(length))), 0, 0]){
		union(){
			cube([2 + 4*len(str(length)), depth, 2]);
			translate([2, 2, 1])
				write(str(length), t=2, h=5);
		}
	}
}

module make_bridge(width, depth, height, length, thickness){
	union(){
		anchors(width, depth, height, length);
		bridge(width, depth, height, length, thickness);
		if (depth >= 10){
			write_length(depth, length);
		}
	}
}

width = 2;
depth = 10;
height = 10;
length = 80;
thickness = 2;
make_bridge(width, depth, height, length, thickness);
