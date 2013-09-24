//DUALLLLLL
$fn = 50;

spacing = .0001;
support_angle = 68;
shell_thickness = .4;
layer_thickness = .2;

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
			}
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
	}
}

block(50,1);