module fence(num_planks, plank_width, plank_thickness, plank_height, spacing, connector_height){
	union(){
		for (i=[0:num_planks-1]){
			translate([i*(spacing + plank_width), 0, 0])
				cube([plank_width, plank_thickness, plank_height]);
		}
		translate([-plank_width, 0, .5*(plank_height - connector_height)])
			cube([num_planks * (plank_width + spacing) + spacing, plank_thickness, connector_height]);
	}
}

num_planks = 5;
plank_width = 10;
plank_thickness = 10;
plank_height = 50;
spacing = 10;
connector_height = 10;

fence(num_planks, plank_width, plank_thickness, plank_height, spacing, connector_height);