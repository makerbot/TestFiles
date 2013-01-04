h1 = 7;
h2 = 5;
border = 20;
width = 20;
length = 40;

borderadd = 2*border;

difference(){
	union(){
		cube([width+borderadd,length+borderadd,h1]);
		//translate([0,length,0]) cube([length+borderadd,width+borderadd,h1]);
	}
	translate([border,border,h1-h2])
	union(){
		cube([width,length,h2]);
		//translate([0,length,0]) cube([length,width,h2]);
	}
}