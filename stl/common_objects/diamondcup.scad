pi = 3.1415926535897932384626433832795028841971693993751058209;
fn=80;

polypoints=[[0,-0.5],[0.5,0],[0,0.5],[-0.5,0]];

floorheight = 2.0;
wallthickness = 2.0;
wallheight = 80.0;
radius = 40.0;
diamondh=7;
diamondw=7;
diamondm=1.5;

module diamond(xyz){
	scale(xyz){
		linear_extrude(height=1, slices=2, center=true)
		polygon(points=polypoints);
	}
}

module diamondring(radius, multiple, dxyz){
	for(ang=[0:
				360/(floor(multiple*pi*radius/dxyz[0]))
				:360]){
		rotate([0,0,ang])
		translate([0,radius,0])
		rotate([90,0,0])
		diamond(dxyz);
	}
}

module diamondtower(drm, dxyz, h){
	for(i=[0:floor(h/dxyz[1])]){
		translate([0,0,dxyz[1]*i])
		rotate([0,0,360/(floor(drm[1]*pi*drm[0]/dxyz[0]))*i/2])
		diamondring(drm[0], drm[1], dxyz);
	}
}


difference(){
	cylinder(r=radius+wallthickness, h=wallheight+floorheight, $fn=fn);
	translate([0,0,floorheight])
	cylinder(r=radius, h=wallheight+floorheight, $fn=fn);
	translate([0,0,floorheight+diamondh/2])
	diamondtower([radius, diamondm], [diamondw,diamondh,wallthickness*2], 
			wallheight-diamondh);
}


