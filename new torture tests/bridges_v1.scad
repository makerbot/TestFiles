//BRIDGESSSS
//enclosed convex
//enclosed concave
//single anchor (C)
//S anchor
//chair
//one-to-one
//one-to-many
//many-to-many

//make wedge wider
//convex/concave bridges... 

thickness = 2;
height = 8;				//this includes the base height
baseHeight = 1.5;
outset = 15;

angles = [-20, 0, 20];	//order least to greatest...

d1 = 20;
d2 = 30;
width = 5;
spacing = 3;

$fn = 50;

baseLength = 2*max(d1,d2) + outset;

module addBase()
{
	union(){
		translate([0,0,.5*baseHeight]) cube([baseLength, baseLength, baseHeight], center=true);
		child();
	}
}


module enclosedConvex(radius)
{
	difference(){
		addBase() cylinder(height, radius, radius, 0);
		translate([0,0,-thickness]) cylinder(height, radius-thickness, radius-thickness, 0);
	}
}

module enclosedConcave(width, depth)
{
	difference(){
		addBase()
		translate([.5*outset, 0,0])
		union(){
			translate([0,0, .5*height]) cube([width, depth, height], center=true);
			translate([0,0, .5*height]) cube([depth, width, height], center=true);
		}
		translate([.5*outset, 0,0])
		union(){
			translate([0,0,-thickness+.5*height]) cube([width-2*thickness, depth-2*thickness, height], center=true);
			translate([0,0,-thickness+.5*height]) cube([depth-2*thickness, width-2*thickness, height], center=true);
		}
	}
}

module singleAnchor(radius)
{
	difference(){
		addBase() cylinder(height, radius, radius, 0);
		translate([0,0,-thickness]) cylinder(height, radius-thickness, radius-thickness, 0);
		translate([-2*(radius+outset), 0, -radius]) cube(4*(radius+outset));
	}
}

module SAnchor(r1, r2)
{
	assign(height = 2*height)
	translate([r1,0,0])
	union(){
		difference(){
			cylinder(height, r1, r1, 0);
			translate([0,0,-thickness])  cylinder(height, r1-thickness, r1-thickness, 0);
			translate([-50, -2*50-.1, -50]) cube(100);
		}

		translate([r1+r2-thickness, 0, 0]) 
		difference(){
			cylinder(height, r2, r2, 0);
			translate([0,0,-thickness]) cylinder(height, r2-thickness, r2-thickness, 0);
			translate([-50, .001, -50]) cube(100);
		}

		translate([-r1,-r2,0]) cube([thickness, r2, height]);
		translate([-r1,-r2,height-thickness]) cube([2*r1+r2-thickness, r2, thickness]);
		translate([r1+2*(r2-thickness),0,0]) cube([thickness,.5*r1,height]);
		translate([0,0,height-thickness]) cube([r1+2*r2-thickness, .5*r1, thickness]);
	}
}

module chair(width, depth, legThickness)
{
	//addBase(width, depth, false)
	union(){
		cube([legThickness, legThickness, height]);
		translate([0, depth-legThickness, 0]) cube([legThickness, legThickness, height]);
		translate([width-legThickness, 0, 0]) cube([legThickness, legThickness, height]);
		translate([width-legThickness, depth-legThickness, 0]) cube([legThickness, legThickness, height]);
		translate([0,0,height-thickness]) cube([width, depth, thickness]);
	}
}

module oneToOne(length, width, spacing)
{	union(){
		rotate([0,0,-90]){
			assign(spacing=width+spacing)
			for (i=[0:len(angles)-1])
			{
				translate([i*spacing+width,0,0]) cube([width, thickness, height]);
				translate([i*spacing+width+length*sin(angles[i]),length*cos(angles[i]), 0]) 
					cube([width, thickness, height]);
				translate([0,0,height-thickness])
				linear_extrude(height=thickness)
				polygon([	[i*spacing+width,thickness],
							[i*spacing+2*width,thickness],
							[i*spacing+2*width+length*sin(angles[i]),length*cos(angles[i])],
							[i*spacing+width+length*sin(angles[i]),length*cos(angles[i])]
						]);
			}
		}
	}
}

module oneToMany(length, width, spacing)
{
	union(){
		rotate([0,0,-90]){
			translate([width,0,0]) cube([width*len(angles)+spacing*(len(angles)-1), thickness, height]);
		
			assign(spacing=width+spacing)	
			for (i=[0:len(angles)-1])
			{
				translate([i*spacing+width+length*sin(angles[i]),length*cos(angles[i]), 0]) 
					cube([width, thickness, height]);
				translate([0,0,height-thickness])
				linear_extrude(height=thickness)
				polygon([	[i*spacing+width,thickness],
							[i*spacing+2*width,thickness],
							[i*spacing+2*width+length*sin(angles[i]),length*cos(angles[i])],
							[i*spacing+width+length*sin(angles[i]),length*cos(angles[i])]
						]);
			}
		}
	}
}

module manyToMany(length, width, spacing)
{	
	union(){
		rotate([0,0,-90]){
			translate([width,0,height-thickness]) cube([width*len(angles)+spacing*(len(angles)-1), thickness, thickness]);
	
			assign(spacing=width+spacing)
			for (i=[0:len(angles)-1])
			{
				translate([i*spacing+width,0,0]) cube([width, thickness, height]);
				translate([i*spacing+width+length*sin(angles[i]),length*cos(angles[i]), 0]) 
					cube([width, thickness, height]);
				translate([0,0,height-thickness])
				linear_extrude(height=thickness)
				polygon([	[i*spacing+width,thickness],
							[i*spacing+2*width,thickness],
							[i*spacing+2*width+length*sin(angles[i]),length*cos(angles[i])],
							[i*spacing+width+length*sin(angles[i]),length*cos(angles[i])]
						]);

				if(i<len(angles)){
					translate([0,0,height-thickness])
					linear_extrude(height=thickness)
					polygon([	[i*spacing+2*width+length*sin(angles[i]),length*cos(angles[i])],
								[i*spacing+2*width+length*sin(angles[i]),length*cos(angles[i])+thickness],
								[(i+1)*spacing+width+length*sin(angles[i+1]),length*cos(angles[i+1])+thickness],
								[(i+1)*spacing+width+length*sin(angles[i+1]),length*cos(angles[i+1])]
							]);
				}
			}
		}
	}
}

module wedge(r1,r2, angle)
{
	difference(){
		union(){
			difference(){
				cylinder(height, r1,r1, 0);
				translate([0,0,-.001]) cylinder(height-thickness, r1-thickness, r1-thickness, 0);
			}
			cylinder(height, r2+thickness, r2+thickness, 0);
		}
		cylinder(2*height, r2,r2, 0, center=true);
		translate([-2*r1,0,0]) cube(4*r1, center=true);
		rotate([0,0,-angle]) translate([2*r1,0,0]) cube(4*r1, center=true);
	}
}

translate([-50,-70,0])
difference(){
	union(){
		translate([.5*baseLength,.5*baseLength,0]) enclosedConvex(d1);
		translate([1.5*baseLength,.5*baseLength,0]) enclosedConcave(d1,d2);
		translate([1.5*baseLength, 1.5*baseLength,0]) singleAnchor(d1);
		translate([d1+outset-d2,d1+outset,0]) SAnchor(d2,.75*d1);
		translate([0, baseLength,0]) chair(baseLength,.5*baseLength, width);
		translate([baseLength+2*outset,baseLength+outset,0]) oneToMany(d2, width, spacing);
		translate([baseLength+2*outset,baseLength+outset,height]) oneToOne(d2, width, spacing);
		translate([baseLength+2*outset,baseLength+outset,2*height]) manyToMany(d2, width, spacing);
		translate([baseLength+.5*outset,baseLength-outset,0]) wedge(d2+7,10,15);

	}
	//change these eventually
	translate([-baseLength,-.01,-50]) cube([4*baseLength, outset, 100]);
	translate([2*baseLength-10,0,-50]) cube([2*outset,3*baseLength, 100]);

	//cut some corners for less warping (hopefully)
	translate([-.1, outset-.1, -baseHeight])
	linear_extrude(height=3*baseHeight) polygon([[0,0], [0,7], [7,0]]);

	translate([2*baseLength-10+.1, outset-.1, -baseHeight])
	rotate([0,0,90])
	linear_extrude(height=3*baseHeight) polygon([[0,0], [0,7], [7,0]]);
	
	translate([2*baseLength-10+.1, 1.5*baseLength+.1, -baseHeight])
	rotate([0,0,180])
	linear_extrude(height=3*baseHeight) polygon([[0,0], [0,7], [7,0]]);
}