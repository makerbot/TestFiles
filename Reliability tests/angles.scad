include <Write.scad>

module base(width, depth, height, angle){
	translate([-width, 0, 0])
		difference(){
			cube([width, depth, height]);
			if (width >= 10 && depth >= 10)
				translate([2, 2, height-1])
					write(str(angle), t=height, h=5);
		}
}

module angle_block(depth, height, angle){
	rotate([-90, 0, 0]){
		linear_extrude(height=depth)
			polygon([[0, 0], [0, -height], [height*tan(angle), -height]]);
	}
}

module angle_block_with_base(width, depth, height, angle){
	union(){
		base(width, depth, height, angle);
		angle_block(depth, height, angle);
	}
}

width = 10;
depth = 10;
height = 10;
angle = 60;
angle_block_with_base(width, depth, height, angle);
