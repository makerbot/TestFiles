//DUALLLLLL
$fn = 50;

spacing = .0001;
support_angle = 68;
shell_thickness = .4;
layer_thickness = .2;
//add cube offset factor here

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
	for(ring = [0:num_rings-1]){
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
		alternating_block(2, 2, 2, radius, height, odd);
		
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
		translate([layer * (width + spacing), 0, 0])
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
		translate([0, anchor_thickness, height - bridge_thickness]) 
		cube([width, length - 2*anchor_thickness, bridge_thickness]);
	}
}

module alternating_center_bridge(num_layers, length, width, height, bridge_thickness, anchor_thickness, piece){
	for(layer = [0:num_layers-1]){
		translate([layer * (width + spacing), 0, 0])
		if((layer % 2) == piece){
			center_bridge(length, width, height, bridge_thickness, anchor_thickness, 1);
		}
		else{
			center_bridge(length, width, height, bridge_thickness, anchor_thickness, 0);
		}
	}
}

module star_point(radius, height){
	angle = 360/10;
	linear_extrude(height = height)
	polygon([[0, 0], [.4*radius * tan(angle), .4*radius], [0, radius], [-.4*radius * tan(angle), .4*radius]]);
}

module star(radius, height){
	angle = 360/5;
	union(){
		for(i = [0:5]){
			rotate([0, 0, i*angle])
			translate([0, -.0001, 0])
			star_point(radius, height);
		}
	}
}

module dots(size, height){
	num = size/shell_thickness;
	for(i = [0:num-1]){
		if((i % 4) == 0){
			translate([0, i * shell_thickness, 0])
			for(j = [0:num-1]){
				if((j % 4) == 0){
					translate([j * shell_thickness, 0, 0])
					cube([shell_thickness, shell_thickness, height]);
				}
			}
		}
	}
}

module cube_face_1(size, height){
	offset = .1 * size;
	assign(size = size - 2*offset)

	translate([offset, offset, 0]){
		difference(){
			cube([.45 * size, .45 * size, height]);
			translate([shell_thickness, shell_thickness, 0])
			cube([.45*size - 2*shell_thickness, .45*size - 2*shell_thickness, height]);
		}
		dots(.45*size, height);

		translate([.45*size + offset, 0, 0])
		difference(){
			cube([.45*size, .45*size, height]);
			translate([.225*size, .215*size, 0]) star(.2*size);
		}

		translate([0, .45*size + offset, 0])
		cube([.45*size, .45*size, height]);

		translate([(.225+.45)*size + offset, (.225+.45)*size + offset, 0])
		star(.225 * size, height);
	}
}

module cube_face_2(size, depth){
	offset = .1 * size;
	translate([.5 * size, .5 * size, 0])
	assign(size = size - 2*offset){
		translate([0, 0, .5*depth]) 
		union(){
			rotate([0, 0, 45]) cube([size, shell_thickness, depth], center=true);
			rotate([0, 0, -45]) cube([size, shell_thickness, depth], center=true);
		}
	}
}

module cube_face_domes(size){
	offset = .1 * size;
	radius = .175 * size;
	translate([radius, 0, radius])
	scale([1, .5, 1])
	for(i = [0:1])
	{	translate([0, 0, i*(2*radius + offset)])
		for(j = [0:1])
		{
			translate([j*(2*radius + offset), 0, 0]) sphere(radius);
		}
	}
}

module cube_face_3(size, piece){
	offset = .1 * size;
	translate([offset, 0, offset])
	if(piece == 1){
		union(){
			difference(){
				cube_face_domes(size);
				translate([.175*size, 0, .175*size]) cube(2*.1*size, center=true);
				translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size, center=true);
				translate([.175*size, 0, 3*.175*size + offset]) sphere(.7*.175*size);
			}
			intersection(){
				cube_face_domes(size);
				translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size - 2*shell_thickness, center=true);
			}
		}
	}

	else{
		intersection(){
			cube_face_domes(size);
			union(){
				translate([.175*size, 0, .175*size]) cube(2*.1*size, center=true);
				difference(){
					translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size, center=true);
					translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size - 2*shell_thickness, center=true);
				}
			}
		}
		translate([.175*size, 0, 3*.175*size + offset]) sphere(.7*.175*size);
	}
}

module cube_face_cylinders(size){
	offset = .1 * size;
	radius = .175 * size;
	translate([radius, 0, radius])
	for(i = [0:1])
	{	translate([0, 0, i*(2*radius + offset)])
		for(j = [0:1])
		{
			translate([j*(2*radius + offset), 0, 0])
			rotate([-90, 0, 0]) 
			cylinder(.5*radius, radius, radius);
		}
	}
}

module cube_face_4(size, piece){
	offset = .1 * size;
	radius = .175 * size;
	translate([offset, 0, offset])
	if(piece == 1){
		difference(){
			difference(){
				cube_face_cylinders(size);
				translate([.175*size, 0, .175*size]) cube(2*.1*size, center=true);
				translate([.175*size, .5*.7*.175*size, 3*.175*size + offset]) scale([1, .5, 1]) sphere(.7*.175*size);
				difference(){
					translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size, center=true);
					translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size - 2*shell_thickness, center=true);
				}
			}
			cube_face_domes(size);
		}
	}
	else{
		difference(){
			union(){
				difference(){
					translate([0, .1*size, 0])
					union(){
						translate([.175*size, 0, .175*size]) cube(2*.1*size, center=true);
						difference(){
							translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size, center=true);
							translate([3*.175*size + offset, 0, .175*size]) cube(2*.1*size - 2*shell_thickness, center=true);
						}
					}
					cube_face_domes(size);
				}
				translate([.175*size, .5*.7*.175*size, 3*.175*size + offset]) scale([1, .5, 1]) sphere(.7*.175*size);
			}
		translate([0, .5*.175 * size, 0]) cube(size);
		}
	}
}


module block(size, piece){
	offset = .1 * size;
	if(piece == 0){
		union(){	
			difference(){
				cube(size);
				//bottom
				cube_face_1(size, layer_thickness);
				//top
				translate([0,0,size-layer_thickness+spacing]) cube_face_1(size, layer_thickness);
				//front
				translate([0, shell_thickness-spacing, 0]) rotate([90, 0, 0]) cube_face_2(size, shell_thickness);
				//back
				translate([0, size + spacing, 0]) rotate([90, 0, 0]) cube_face_1(size, shell_thickness);
				translate([0, offset, offset]) rotate([0, 0, 90]) cube_face_domes(size);
				translate([size+spacing, offset, offset]) rotate([0, 0, 90]) cube_face_cylinders(size);		
			}
			//left
			rotate([0, 0, 90]) cube_face_3(size, 0);
			//right
			translate([size, 0, 0]) rotate([0, 0, 90]) cube_face_4(size, 0);
		}
	}
	else{
		//bottom
		cube_face_1(size, layer_thickness);
		//top
		translate([0,0,size-layer_thickness+spacing]) cube_face_1(size, layer_thickness);
		//front
		translate([0, shell_thickness-spacing, 0]) rotate([90, 0, 0]) cube_face_2(size, shell_thickness);
		//back
		translate([0, size + spacing, 0]) rotate([90, 0, 0]) cube_face_1(size, shell_thickness);	
		//left
		rotate([0, 0, 90]) cube_face_3(size, 1);
		//right
		translate([size, 0, 0]) rotate([0, 0, 90]) cube_face_4(size, 1);	
	}
}

module alternating_dome(num_layers, radius, height, odd){
	scale([1, 1, height/radius])
	intersection(){
		difference(){
			sphere(radius);
			translate([0, 0, -radius]) cube(2*radius, center=true);
		}
		translate([-radius, -radius, 0]) alternating_block(1, 1, num_layers, 2*radius, radius/num_layers, odd);
	}
}

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

//cube_face_1(50, 20);
//cube_face_3(50, 0);
//cube_face_3(50, 1);
//cube_face_4(50, 0);
//cube_face_4(50, 1);

block(50, 0);
//block(50, 1);

//alternating_dome(5, 50, 20, 1);

//block
//alternating_block(3, 3, 3, 10, 10, 0);
//alternating_block(3, 3, 3, 10, 10, 1);

//pillars
//alternating_pillar_block(3, 3, 3, 2.5, 5, 10, 0);
//alternating_pillar_block(3, 3, 3, 2.5, 5, 10, 1);

//circles
//stacked_alternating_circles(4, 4, 3, 3, 0);
//stacked_alternating_circles(4, 4, 3, 3, 1);

//center bridge
//alternating_center_bridge(3, 40, 10, 5, 3, 3, 0);
//alternating_center_bridge(3, 40, 10, 5, 3, 3, 1);

//top bridge
//alternating_top_bridge(3, 40, 10, 5, 3, 3, 0);
//alternating_top_bridge(3, 40, 10, 5, 3, 3, 1);

//supports
//alternating_supports_block(15, 10, 0);
//alternating_supports_block(15, 10, 1);