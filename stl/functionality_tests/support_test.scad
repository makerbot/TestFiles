
union() {
difference() {
  rotate([0, 45, 0])
  cube(size = [5, 10, 20], center=false);

  translate([0, 0, -100])
  cube(size = [100, 100, 100], center=false);
}

translate([0, 0, 10])
cube(size =[25, 10, 5], center=false);
}