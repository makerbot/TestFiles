
//DUALLLLLL

spacing = .000001;
support_angle = 68;
shell_thickness = .4;
layer_thickness = .2;

module alternating_row(num, width, height, odd){
	for(col = [0:num-1]){
		if((col % 2) == odd){
			translate([col * (width+spacing),0,0]) 
			cube([width, width, height]);
		}
	}
}

module alternating_grid(num_rows, num_cols, width, height, odd){
	for (col = [0:num_cols-1]){
		translate([0, col * (width+spacing), 0])
		if((col % 2) == odd){
			alternating_row(num_rows, width, height, 1);
		}
		else{
			alternating_row(num_rows, width, height, 0);
		}
	}
}

module alternating_block(num_rows, num_cols, num_layers, width, height, odd){
	//odd = 1 for, starting row of starting layer, odd squares present.
	//odd = 0 for, starting row of starting layer, even squares present

	for (layer = [0:num_layers-1]){
		translate([0, 0, layer * (height+spacing)])
		if ((layer % 2) == odd){
			alternating_grid(num_rows, num_cols, width, height, 1);
		}
		else{
			alternating_grid(num_rows, num_cols, width, height, 0);
		}
	}
}

//WIP
module alternating_scaled_layers(num_layers, width, height, scale, odd){
	n = 0;
	for(layer = [0:num_layers-1]){
		assign(n = n + layer){
		if (layer % 2 == odd){
			
			cube([width, width, scale*height + spacing]);
		}
		echo(n);}
	}
}

module alternating_concentric_circles(num_rings, thickness, height, odd){
	for(ring = [0:num_rings-2]){
		if((ring % 2) == odd){
			difference(){
				cylinder(height, (ring+1) * thickness, (ring+1) * thickness);
				cylinder(height+.1, ring * (thickness+spacing), ring * (thickness+spacing));
			}
		}
	}
}

module stacked_alternating_circles(num_rings, num_layers, thickness, height, odd){
	for(layer = [0:num_layers]){
		translate([0, 0, layer * (height+spacing)])
		if((layer % 2) == odd){
			alternating_concentric_circles(num_rings, thickness, height, 1);
		}
		else{
			alternating_concentric_circles(num_rings, thickness, height, 0);
		}
	}
}

module alternating_pillar_line(num_rows, radius, height, spacing, odd){
	for(row = [0:num_rows-1]){	
		if((row % 2) == odd){
			translate([row * spacing, 0, 0])
			cylinder(height, radius, radius);
		}
	}
}

module alternating_pillar_grid(num_rows, num_cols, radius, height, spacing, odd){
	for(col = [0:num_cols-1]){
		translate([0, col * spacing, 0])
		if((col % 2) == odd){
			alternating_pillar_line(num_rows, radius, height, spacing, 1);
		}	
		else{
			alternating_pillar_line(num_rows, radius, height, spacing, 0);
		}
	}
}

module alternating_pillar_block(num_rows, num_cols, num_layers, radius, height, spacing, odd){
	for(layer = [0:num_layers-1]){
		translate([0, 0, layer * height])
		if((layer % 2) == odd){
			alternating_pillar_grid(num_rows, num_cols, radius, height, spacing, 1);
		}	
		else{
			alternating_pillar_grid(num_rows, num_cols, radius, height, spacing, 0);
		}
	}
}

module supports_block(radius, height){
	union(){
		cylinder(height, radius, radius + height*tan(support_angle - 1));
		assign(radius = radius + height*tan(support_angle - 1))
		translate([0, 0, height + spacing]) 
		cylinder(height, radius, radius + height*tan(support_angle + 1));
	}
}

module alternating_supports_block(radius, height, odd){
	intersection(){
		supports_block(radius, height);
		assign(radius = (radius + height*tan(support_angle - 1)) + height*tan(support_angle + 1))
		translate([-radius, -radius, -spacing * height]) 
		scale([1, 1, 1 + spacing])
		%alternating_block(2, 2, 2, radius, height, odd);
		
	}
}

module top_bridge(length, width, height, bridge_thickness, anchor_thickness, piece){
	//piece 0 = anchors
	//piece 1 = bridge
	if(piece == 0){
		cube([width, anchor_thickness, height - bridge_thickness]);
		translate([0, length - anchor_thickness, 0]) cube([width, anchor_thickness, height - bridge_thickness]);
	}
	else{
		translate([0, 0, height - bridge_thickness + spacing]) cube([width, length, bridge_thickness]);
	}
}

module alternating_top_bridge(num_layers, length, width, height, bridge_thickness, anchor_thickness, piece){
	for(layer = [0:num_layers-1]){
		translate([width * layer, 0, 0])
		if((layer % 2) == piece){
			top_bridge(length, width, height, bridge_thickness, anchor_thickness, 1);
		}
		else{
			top_bridge(length, width, height, bridge_thickness, anchor_thickness, 0);
		}
	}
}

module center_bridge(length, width, height, bridge_thickness, anchor_thickness, piece){
	if(piece == 0){
		cube([width, anchor_thickness, height]);
		translate([0, length - anchor_thickness, 0]) cube([width, anchor_thickness, height]);
	}
	else{
		translate([0, anchor_thickness, height - bridge_thickness + spacing]) cube([width, length - 2* anchor_thickness, bridge_thickness]);
	}
}

module alternating_center_bridge(num_layers, length, width, height, bridge_thickness, anchor_thickness, piece){
	for(layer = [0:num_layers-1]){
		translate([width * layer, 0, 0])
		if((layer % 2) == piece){
			center_bridge(length, width, height, bridge_thickness, anchor_thickness, 1);
		}
		else{
			center_bridge(length, width, height, bridge_thickness, anchor_thickness, 0);
		}
	}
}

module star_point(radius){
	angle = 360/10;
	linear_extrude(height = layer_thickness)
	polygon([[0, 0], [.5*radius * tan(angle), .5*radius], [0, radius], [-.5*radius * tan(angle), .5*radius]]);
}

module star(radius){
	angle = 360/5;
	union(){
		for(i = [0:5]){
			rotate([0, 0, i*angle])
			star_point(radius);
		}
	}
}

module cube_top_bottom_face(size){
	offset = .1 * size;
	assign(size = size - 2*offset)

	translate([offset, offset, 0]){
		difference(){
			cube([.5 * size, .4 * size, layer_thickness]);
			translate([shell_thickness, shell_thickness, 0])
			cube([.5*size - 2*shell_thickness, .4*size - 2*shell_thickness, layer_thickness]);
		}
	
		translate([.5*size + offset, 0, 0])
		difference(){
			cube([.4*size, .4*size, layer_thickness]);
			translate([.5*radius, .5*radius, 0]) star(.2*size);
		}
	}
}

/*
module cube(size, piece){
	if(piece == 0){
		cube(size);
	}
	else{
		
	}
}*/

//alternating_block(5, 5, 10, 10, 5, 1);

//alternating_concentric_circles(10, 5, 5, 1);
//stacked_alternating_circles(10, 10, 5, 5, 0);

//alternating_pillar_block(20, 10, 10, 10, 5, 10, 0);

//supports_block(10,10);
//alternating_supports_block(10, 10, 0);

//bridge1
//top_bridge(20, 10, 10, 2, 3, 0);
//#top_bridge(20, 10, 10, 2, 3, 1);

//alternating_top_bridge(3, 20, 10, 10, 2, 3, 0);
//#alternating_top_bridge(3, 20, 10, 10, 2, 3, 1);

//bridge2
//center_bridge(20, 10, 10, 2, 3, 0);
//#center_bridge(20, 10, 10, 2, 3, 1);

//alternating_center_bridge(3, 20, 10, 10, 2, 3, 0);
//#alternating_center_bridge(3, 20, 10, 10, 2, 3, 1);

cube_top_bottom_face(50);
