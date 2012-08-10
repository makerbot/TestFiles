fn=300;

footradius = 30;
footheight = 1.0;
footheight2 = 3.0;
cuplower = 28;
cupupper = 35;
cupheight = 80;
cupwall = 1.5;

points = [[0,0],
		[footradius,0],
		[footradius,footheight],
		[cuplower,footheight2],
		[cupupper,cupheight],
		[0,cupheight]];
points2 = [[0,footheight2],
		[cuplower-cupwall,footheight2],
		[cupupper-cupwall,cupheight],
		[0,cupheight]];
rotate_extrude(convexity = 4, $fn=fn)
difference(){
	polygon(points);
	polygon(points2);
}