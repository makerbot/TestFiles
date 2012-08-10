module ramp(dimentions, center=false) {
	points = [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,1,1],[1,1,1]];
	triangles = [[0,1,2],[0,2,3],[0,3,4],[5,2,1],[3,2,5],[5,4,3],[5,1,0],[0,4,5]];
	scale(dimentions){
		if(center) {
			translate([-0.5,-0.5,-0.5])
			polyhedron(points = points, triangles = triangles, convexity = 1);
		} else {
			polyhedron(points = points, triangles = triangles, convexity = 1);
		}
	}
}

module sloped_roof(dimentions, roofheight) {
	union() {
		cube(dimentions);
		translate([0,0,dimentions[2]])
		ramp([dimentions[0],dimentions[1],roofheight]);
	}
}

module double_roof(dimentions, roofheight) {
	sloped_roof(dimentions, roofheight);
	translate([max(dimentions[0],dimentions[1]),max(dimentions[0],dimentions[1])*1.2,0])
	rotate([0,0,90])
	sloped_roof(dimentions, roofheight);
}

dimentions = [15,15,2];
roofstart = 2;
roofstep = 2;

istart = 0;
iend = 1;

spacing = 20;

translate([-(0.5*(iend+1-istart))*spacing,0,0])
for(i=[istart:iend]) {
	translate([i*spacing,0,0])
	double_roof(dimentions, roofstart+i*roofstep);
}