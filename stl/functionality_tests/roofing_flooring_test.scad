module roofing_test(bottom_dims, top_dims, top_offset) {
	cube(bottom_dims);
	translate([top_offset,0,bottom_dims[2]])
	cube(top_dims);
}

module roofing_test_bothways(bottom_dims, top_dims, top_offset) {
	rotate([0,0,90])
	roofing_test(bottom_dims, top_dims, top_offset);
	translate([-bottom_dims[0],bottom_dims[1]+top_offset+2,0])
	roofing_test(bottom_dims, top_dims, top_offset);
}

bottom_dims = [10,10,2];
top_dims = [10,10,2];
offset_start = 1.0;
offset_step = 0.5;
spacing = 15;

translate([-30,0,0])
for(i=[0:4]){
	translate([bottom_dims[0]+offset_start+i*offset_step+i*spacing,0,0])
	roofing_test_bothways(bottom_dims,top_dims,offset_start+i*offset_step);
}