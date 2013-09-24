spur_width = .4;

module make_dots(num_rows, num_cols, size, spacing){
	for(row = [0:num_rows-1]){
		translate([row * (spacing + size), 0, 0])
		for(col = [0:num_cols-1]){
			translate([0, col * (spacing + size), 0])
			cube(size);
		}
	}
}

module make_dot_cube(num_rows, size, spacing){
	//bottom
	make_dots(num_rows, num_rows, size, spacing);
	//front
	translate([0, -spacing + size, spacing]) 
		rotate([90, 0, 0]) 
			make_dots(num_rows, num_rows, size, spacing);
	//back
	translate([0, num_rows * (spacing + size), spacing]) 
		rotate([90, 0, 0]) 
			make_dots(num_rows, num_rows, size, spacing);
	//left
	translate([-spacing, 0, spacing]) 
		rotate([90, 0, 90]) 
			make_dots(num_rows, num_rows, size, spacing);
	//right
	translate([num_rows * (spacing + size) - size, 0, spacing]) 
		rotate([90, 0, 90]) 
			make_dots(num_rows, num_rows, size, spacing);
	//top
	translate([0, 0, num_rows * (spacing + size) + spacing - size]) 
		make_dots(num_rows, num_rows, size, spacing);
}

module negative_dot_cube(num_rows, size, spacing){
	difference(){
		translate([-spacing, -spacing, 0]) 
			cube(num * (size + spacing) + spacing);
		make_dot_cube(num, size, spacing);
	}
}

spacing = spur_width + 1;
size = spur_width;
num = 10;


//negative_dot_cube(num, size, spacing);
make_dot_cube(num, size, spacing);
