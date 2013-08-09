ws = 10.0;
ats = 10.0;
ahs = 3.0;
bts = 2.0;
linit = 10;
lstep = 5;
lcount = 10;

module makebridge(w,l,at,ah,bt) {
	epsilon = 0.01;
	union() {
		cube([at,w,ah + bt]);
		translate([at - epsilon,0,ah])
		cube([l + 2 * epsilon,w,bt]);
		translate([at+l,0,0])
		cube([at,w,ah + bt]);
	}
}

rotate([0,0,30])
for(ls = [0:lcount]) {
	translate([0,ls * (ws + 5.0), 0])
	makebridge(ws,linit + ls*lstep, ats, ahs, bts);
}