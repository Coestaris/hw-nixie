/*
SHOU HAN TYPE-C 6P(073) generated-envelope model.
Evidence: manufacturer drawing page 1, Rev.A, units mm. Coordinate system
matches the rev2 footprint: six contacts at Y=+2.125, shell anchors at
X=+/-4.32, and the receptacle mouth faces -Y. Z=0 is the PCB seating plane.
*/
$fa = 4;
$fs = 0.12;
render_part = "all";
projection_view = "3d";

shell_x = 8.94;
shell_y = 7.15;
shell_z = 3.20;
shell_t = 0.25;
rear_y = 2.475;
front_y = rear_y-shell_y;
contact_x = [-2.75,-1.52,-0.50,0.50,1.52,2.75];

shell_color = [0.72,0.74,0.76];
insert_color = [0.10,0.10,0.11];
contact_color = [0.84,0.65,0.16];

module shell() {
    difference() {
        translate([-shell_x/2,front_y,0]) cube([shell_x,shell_y,shell_z]);
        translate([-4.05,front_y-0.01,0.55]) cube([8.10,shell_y-shell_t+0.02,2.15]);
    }
    for (x=[-4.32,4.32]) for (y=[-2.125,1.675])
        translate([x-0.25,y-0.60,-1.20]) cube([0.50,1.20,1.35]);
}

module insert() {
    translate([-3.85,front_y+0.35,0.72]) cube([7.70,5.55,1.55]);
    translate([-3.20,front_y-0.02,1.10]) cube([6.40,1.60,0.65]);
}

module contacts() {
    for (x=contact_x) {
        translate([x-0.30,1.525,0.02]) cube([0.60,1.20,0.12]);
        translate([x-0.16,0.65,0.12]) cube([0.32,1.05,0.70]);
    }
}

module selected_model() {
    if (render_part == "shell" || render_part == "all") color(shell_color) shell();
    if (render_part == "insert" || render_part == "all") color(insert_color) insert();
    if (render_part == "contacts" || render_part == "all") color(contact_color) contacts();
}

if (projection_view == "top") projection(cut=false) selected_model();
else if (projection_view == "front") projection(cut=false) rotate([90,0,0]) selected_model();
else if (projection_view == "side") projection(cut=false) rotate([90,0,90]) selected_model();
else selected_model();
