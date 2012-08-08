fn=300;
rs = 10;
rb = 7;
t=0.5;

intersection(){
	translate([0,0,rs])
	cube([rs*2,rs*2,rs*2], center=true);
	sphere(r=rs, $fn=fn);
}