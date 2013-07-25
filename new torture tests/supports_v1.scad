//SUPPOOOOOORTS
$fn=50;
supportAngle=68;
layerHeight=.2;

block_width=10;
block_depth=20;
block_height=20;
block_thickness=3;

cone_radius=20;

star_points=6;

shapes_height=20;
shapes_size=10;

module trapezoid(baseWidth,depth,height, thickness){
	union(){
		linear_extrude(height=depth)
		polygon([[0,0],[height*-tan(supportAngle+1), height],[baseWidth, height], [baseWidth, 0]]);
		translate([baseWidth,0,0]) linear_extrude(height=depth)
		polygon([[0,0],[0, height],[height*tan(supportAngle-1),height]]);
	}
}

module supportBlock(baseWidth,depth,height, thickness){
	rotate([90,0,0])
	union(){
		difference(){
			trapezoid(baseWidth,depth,height, thickness);
			translate([0,thickness,0]) scale([.5,.5,2]) trapezoid(baseWidth,depth,height, thickness);
			cube([baseWidth+height*tan(supportAngle-1),thickness+.5*height,depth]);
			
		}
		cube([height, thickness, depth]);
	}
}

module cone(angle, radius){
	height=radius/tan(angle);
	cylinder(height,0,radius);
}

module funnel(r1, r2, segs=20){
	diff = -(r1-r2);
	segHeight = diff/segs;
	union(){
		for(i=[0:segs-1]){
			translate([0,0,i*segHeight]) cylinder(segHeight, r2-sqrt(pow(diff,2)-pow(i*segHeight,2)), r2-sqrt(pow(diff,2)-pow((i+1)*segHeight,2)));
		}
	}
}

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


supportBlock(10,20,20,3);
translate([0,-.5*block_depth,block_height+.5*layerHeight]) cone(supportAngle+1, cone_radius);
translate([2*cone_radius,-.5*block_depth,block_height+.5*layerHeight]) cone(supportAngle-1, cone_radius);
translate([-2*cone_radius,-.5*block_depth,block_height+.5*layerHeight]) funnel(0,cone_radius);
translate([7*shapes_size,15,0]) shapes(20, supportAngle-1, shapes_height);

