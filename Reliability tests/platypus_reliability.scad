//Reliability 

inch_mm_conversion = 25.4;

width = 10*inch_mm_conversion;
depth = 8*inch_mm_conversion;
height = 5.8*inch_mm_conversion;

thickness = .5*inch_mm_conversion;
spacing = 2;

pi = 3.141592653589793;
to_radians = pi/180;

module sinewave(length, scale, seg){
	segWidth = 360/seg;
	numWaves = floor(length/(2*pi*scale));
	scale([scale,scale,1]){
		for(i=[0:numWaves]){
			translate([i*2*pi-.000001,0,0])
			linear_extrude(height=6*inch_mm_conversion){
				union(){
					for(i=[0:seg]){
						polygon([
							[segWidth*i*to_radians,2+sin(segWidth*i)],
							[segWidth*(i+1)*to_radians,2+sin(segWidth*(i+1))],
							[segWidth*(i+1)*to_radians,0],
							[segWidth*i*to_radians,0]
						]);
					}
				}
			}
		}
	}
}

module sawtooth(length, teethWidth){
	numTeeth = ceil(length/(.8*teethWidth));
	translate([0,.2*teethWidth,0])
	for(i=[0:numTeeth]){
		translate([i*.8*teethWidth,0,0]) rotate([0,0,90]) cylinder(height, .5*teethWidth, .5*teethWidth, $fn=3);
	}
}

module block(){
	for(i=[0:numLayers-1]){
		translate([0,0,i*(thickness+spacing)])
			cube([width,depth,thickness]);
	}
}


numLayers = floor(height/(thickness+spacing));
//echo (numLayers);

difference(){
	block();
	sawtooth(width, 12);
	translate([0,depth,0]) rotate([0,0,-90]) sawtooth(depth, 12);
	translate([width,0,0]) rotate([0,0,90]) sinewave(depth,2,90);
	rotate([0,0,180]) translate([-width,-depth,0]) sinewave(width,2,90);
}