include <Write.scad>

module write_dim(dim){
	translate([2, 2, dim - 1])
		write(str(dim), t=dim, h=5);
}

module make_cube(dim){
	difference(){
		cube(dim);
		if(dim >= 10)
			write_dim(dim);
	}
}

dim = 80;
make_cube(dim);