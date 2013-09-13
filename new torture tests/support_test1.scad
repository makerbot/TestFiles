// Support Test #1
$fn=50;

supportAngle=68;
layerHeight=.2;

star_points=6;

shapes_height=20;
shapes_size=10;

module shapes(size, angle, height){
	star_angle=360/star_points;
	radius=size/2;
	
	rotate([0,0,90]){
		minkowski(){
			cube([size,size,.01], center=true);
			rotate([0,angle,0]) cylinder(height,.01,.01);
		}
	
		translate([0,1*size,0])
		minkowski(){
			scale([1,.5,1]) rotate([0,0,45]) cube([size,size,.01]);
			rotate([0,angle,0]) cylinder(height,.01,.01);
		}
	
		translate([0,3*size,0])
		minkowski(){
			cylinder(.01, radius, radius);
			rotate([0,angle,0]) cylinder(height,.01,.01);
		}
	
		translate([0,5*size,0])
		minkowski(){
			linear_extrude(height=.01)
			union(){
				for(i=[0:star_points]){
					rotate([0,0,i*star_angle]) 
					hull(){
						translate([0,radius,0]) circle(2.5*star_angle/360*radius);
						polygon([[0,radius], [.6*radius*sin(.5*star_angle), .6*radius*cos(.5*star_angle)], [0,0], [-.6*radius*sin(.5*star_angle), .6*radius*cos(.5*star_angle)]]);
					}
				}
			}
			rotate([0,angle,0]) cylinder(height,.01,.01);
		}
	}
}

shapes(20, supportAngle-1, shapes_height);

