union() {
difference() {
  translate([0, 0, -7])
    rotate([0, -45, 0])
    cube(size=[5, 10, 30], center=false);

    translate([-50, -50, -8])
      cube(size = [100, 100, 8], center=false);
}
translate([-30, 0, 13])
  cube(size = [30, 10, 5], center=false);
}