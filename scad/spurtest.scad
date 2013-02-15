x0=3;
union() {
 	cube([42,10,5]);
 	for(x=[x0+1:20]) {
 		translate([(x-x0)*(0.5*sqrt(x)),-5,0])
 		#cube([x/10,10,5]);
 	}
}