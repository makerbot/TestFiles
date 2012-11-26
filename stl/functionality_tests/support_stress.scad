h=3.0;
s=5;
st=0.125;
S=10;
M=10;
fn = 3;
union(){
	for(i=[0:M]){
		rotate([0,0,45*i])
		translate([0,0,i*h]){
			cylinder(r1=S+st*i,r2=S-s+st*i,h=h,$fn=fn);
			rotate([0,0,60])
			cylinder(r1=S+st*i,r2=S-s+st*i,h=h,$fn=fn);
			rotate([0,0,120])
			cylinder(r1=S+st*i,r2=S-s+st*i,h=h,$fn=fn);
		}
	}
}