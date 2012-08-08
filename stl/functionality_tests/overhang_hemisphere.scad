fn=300;
rs = 10;
rb = 7;
t=0.5;

intersection(){
	translate([0,0,rs])
	cube([rs*2,rs*2,rs*2], center=true);
	union(){
		difference(){
			sphere(r=rs, $fn=fn);
			translate([0,0,0]){
				rotate([90,0,0])
				cylinder(r=rb, h=3*rs, center=true, $fn=fn);
				rotate([0,90,0])
				cylinder(r=rb, h=3*rs, center=true, $fn=fn);
			}
		}
		intersection(){
			sphere(r=rs, $fn=fn);
			rotate([0,0,45]){
				cube([rs*3,t,rs*2], center=true);
				cube([t,rs*3,rs*2], center=true);
			}
		}
	}
}