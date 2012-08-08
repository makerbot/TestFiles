module overhang_test(foundation_xyz, foundation_angle, overhang_xyz){

	foundation_bound=[overhang_xyz[0], overhang_xyz[1], foundation_xyz[2]];
	foundation_z=foundation_xyz[2]/cos(foundation_angle);
	foundation_down=foundation_xyz[0]*sin(foundation_angle);
	union(){
		intersection(){
			translate([0,0,(0.5*foundation_z)-(0.0*foundation_down)])
			rotate([0,foundation_angle,0])
			cube([foundation_xyz[0],foundation_xyz[1],foundation_z*10], center=true);
			translate([0,0,foundation_bound[2]/2])
			cube(foundation_bound, center=true);
		}
		translate([0,0,foundation_xyz[2]+overhang_xyz[2]/2])
		cube(overhang_xyz,center=true);
	}
}

x = 50;
y = 10;
z = 10;
gap = 10;

rotate([0,0,90])
for(i=[0:2]){
	translate([0,(-1*(y+gap))+i*(y+gap),0])
	overhang_test([5,y,z], 20+i*20, [x,y,2]);
}