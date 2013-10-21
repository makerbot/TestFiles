
module tiger_half_body(height, body_length, body_width, body_height, leg_width){
	difference(){
		union(){
			cube([body_length, .5 * body_width, body_height]);
			cube([leg_width, leg_width, height]);
			translate([body_length - leg_width, 0, 0])
				cube([leg_width, leg_width, height]);
		}
		translate([.5 * body_length, -body_length + .2 * body_width, -.5 * body_length])
		cylinder(100, 100, 100, $fn=50);
	}
}

module tiger(height, body_length, body_width, body_height, leg_width){
	union(){
		tiger_half_body(height, body_length, body_width, body_height, leg_width);
		translate([body_length - .5 * leg_width, body_width-.0001, 0])
			rotate([0, 0, 180])
				tiger_half_body(height, body_length, body_width, body_height, leg_width);
	}
}	

height = 40;
body_length = 100;
body_width = 30;
body_height = 20;
leg_width = 10;

tiger(height, body_length, body_width, body_height, leg_width);