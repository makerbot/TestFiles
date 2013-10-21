module H(leg_height, leg_width, table_height, table_width, table_thickness){
	union(){
		translate([0, 0, table_height])
			cube([table_width, table_width, table_thickness]);
		cube([leg_width, leg_width, leg_height]);
		translate([table_width - leg_width, 0, 0])
			cube([leg_width, leg_width, leg_height]);
		translate([0, table_width - leg_width, 0])
			cube([leg_width, leg_width, leg_height]);
		translate([table_width - leg_width, table_width - leg_width, 0])
			cube([leg_width, leg_width, leg_height]);
	}
}

leg_height = 100;
leg_width = 10;
table_height = 30;
table_width = 30;
table_thickness = 2;
H(leg_height, leg_width, table_height, table_width, table_thickness);
