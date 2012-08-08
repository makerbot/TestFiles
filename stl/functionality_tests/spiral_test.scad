module spiral_rect(rectsize, height, twist){
	linear_extrude(height=height, convexity=2, twist=twist, slices=height*2)
	square(rectsize, center=true);
}

xspacing = 40;
yspacing = 40;
rectsize = [10,30];
heightstart = 10;
heightmult = 10;
twiststart = 30;
twistmult = 30;

translate([-xspacing, -yspacing, 0])
for(j=[0:2]){
	translate([0,yspacing*j,0])
	for(i=[0:2]){
		translate([xspacing*i,0,0])
		spiral_rect(rectsize,heightstart+j*heightmult,twiststart+i*twistmult);
	}
}