module xspur() {
	cube(size=[0.4, 50, 10], center=false);
}

module yspur() {
	rotate([0, 0, 90])
	translate([0, -50, 0]) xspur();
}

union() {
for (x = [1:4])
  translate([x * 10, 0, 0]) xspur();

for (y = [1:4])
  translate([0, y * 10, 0]) yspur();
}