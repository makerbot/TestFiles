imin = 0;
imax = 3;
smin = 1;
smax = 3;
translate([-15,0,0])
for(i=[imin:imax]){
	translate([15*i,0,0])
	scale([1,lookup(i, [[imin,smin],[imax,smax]]),1])
	cylinder(h=5, r=5, $fn=300);
}