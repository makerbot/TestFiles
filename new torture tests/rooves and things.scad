//ROOVES AND RAAAAFTS
//remember to uncomment hull() before exporting
$fn=30;

dome_sizes=[10,5];
max_dome_size=10;
dome_roundness=[1,.6,.25];

star_radius1=15;
star_radius2=12;

funnel_radius1=5;
funnel_radius2=20;

cone_radius=3;
cone_height=20;

module dome(radius){
	difference(){
		sphere(radius);
		translate([0,0,-2*radius]) cube(4*radius, center=true);
	}
}

module cone(height,radius){
	cylinder(height, radius, 0);
}

module coneArmy(radius, height, num, spacing, scaling=false){
	rotate([0,0,90])
	for(i=[0:num-1]){
		if(scaling == true){
			scale([1,1,(i+1)/num]) translate([i*(spacing+2*radius),0,0]) cone(height,radius);
		}
		else{
			translate([i*(spacing+2*radius),0,0]) cone(height,radius);
		}
	}
}

module starPoint(r1, r2, points, height, segs=20){
	angle=360/points;
	segAngle=90/segs;
	assign(height=height/segs)
	
	union(){
		//hull(){				//uncomment this hull()
		for(i=[0:segs-1]){
			translate([0,0,i*height])
			scale([sqrt(1-pow(i/segs,2)),sqrt(1-pow(i/segs,2)),1]){
				linear_extrude(height=height){
					hull(){
					translate([0,r1,0]) circle(3*angle/360*r1);
					polygon([[0,r1], [r2*sin(.5*angle), r2*cos(.5*angle)], [0,0], [-r2*sin(.5*angle), r2*cos(.5*angle)]]);}
					
				}
			}
		//}						//and this close-bracket
		translate([0,0,height*segs]) cylinder(height,1,1,0);}
	}
}

module makeStar(r1, r2, points, height, segs=20){
	angle=360/points;
	union(){
	for(i=[0:points-1]){
		rotate([0,0,i*angle]) starPoint(r1, r2, points, height);
		}
	}
}

module funnel(r1, r2, height, segs=20){
	diff = -(r1-r2);
	segHeight = diff/segs;
	union(){
		for(i=[0:segs-1]){
			translate([0,0,i*segHeight]) cylinder(segHeight, r2-sqrt(pow(diff,2)-pow(i*segHeight,2)), r2-sqrt(pow(diff,2)-pow((i+1)*segHeight,2)));
		}
	}
}

module coneMob(minRadius, maxRadius, maxX, maxY, height){
	//bools=rands(1,100,maxX*maxY);			//sparse
	bools=rands(1,1,maxX*maxY);				//not sparse....
	radii=rands(minRadius,maxRadius,maxX*maxY,maxX*maxY);



	translate([-2*maxRadius*maxX,0,0])
	for(i=[0:maxX]){
		if(i%2==0){
			for(j=[0:maxY]){
				if(round(bools[i*maxX+j])%2 == 1){
					translate([i*2*maxRadius,j*2*maxRadius,0]) cone(height,radii[i*maxX+j]);
					echo(i*2*maxRadius);
				}
			}
		}
		else{
			translate([0,maxRadius,0])
			for(j=[0:maxY-1]){
				if(round(bools[i*maxX+j])%2 == 1){
					translate([i*2*maxRadius,j*2*maxRadius,0]) cone(height,radii[i*maxX+j]);
					echo(i*2*maxRadius);
				}
			}
		}
	}
}



union(){
	for(i=[0:len(dome_sizes)-1]){
		translate([i*16,0,0])
		for(j=[0:len(dome_roundness)-1]){
			translate([0,j*2*max_dome_size,0]) scale([1,1,dome_roundness[j]]) dome(dome_sizes[i]);
		}
	}
	translate([30+star_radius1,.5*star_radius1,0]) makeStar(star_radius1,star_radius2,7,.75*star_radius1);
	translate([30+star_radius1,1.5*star_radius1+funnel_radius1+10,0]) funnel(funnel_radius1, funnel_radius2, 20);
	translate([-max_dome_size-cone_radius-2,0,0]) coneArmy(cone_radius, cone_height, 5, 5, true);
	translate([-max_dome_size-4*cone_radius,0,0]) coneMob(1.5, cone_radius, 5,7, cone_height);

}
