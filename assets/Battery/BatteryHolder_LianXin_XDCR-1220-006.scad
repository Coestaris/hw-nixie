/*
Lian Xin Technology XDCR-1220-006 CR1220 SMD holder.
Evidence: XDCR-1220-006/007 drawing, page 1, top/side/bottom views,
PCB Holes Diagram, material note, and BOM table (2023-12-25).

Coordinate contract: millimetres; footprint origin is midway between the two
locating-hole X coordinates; +X runs from terminal 1 toward terminal 2, +Y is
across the holder, and Z=0 is the PCB seating plane. The model extends upward
in +Z and locating posts extend below the plane. Terminal 1 is on -X.
*/

$fa = 4;
$fs = 0.25;
epsilon = 0.02;
render_part = "all";
projection_view = "3d";

outer_radius = 7.35;             // diameter 14.7 +/- 0.1
pocket_radius = 6.35;            // diameter 12.7 +/- 0.1
circle_center_x = -1.95;         // 9.3 from left datum to footprint origin
body_left_x = -9.30;
body_right_x = 10.10;            // nominal overall width 19.4
body_half_y = 7.25;              // nominal overall depth 14.5
body_height = 4.15;
base_height = 1.15;
wall_thickness = 1.15;

post_radius = 0.55;              // clearance inside two diameter-1.2 PCB holes
post_depth = 0.80;               // undocumented; fit-check assumption
post_x = [-3.70, 3.80];

terminal_width = 4.50;
terminal_depth = 2.30;
terminal_thickness = 0.25;       // undocumented sheet thickness assumption
terminal_centers_x = [-8.15, 8.55];

housing_color = [0.20, 0.075, 0.025]; // XDCR-1220-006 PPS brown/black-brown
gold_color = [0.83, 0.65, 0.16];      // datasheet: phosphor bronze, Au-plated

module housing() {
    union() {
        difference() {
            translate([circle_center_x, 0, 0])
                cylinder(r=outer_radius, h=base_height);
            translate([circle_center_x, 0, 0.38])
                cylinder(r=pocket_radius, h=base_height + epsilon);
        }

        // Raised insertion-side PPS guide and retaining wall from the side view.
        // These bridges overlap the circular body in XY; disconnected housing
        // volumes are a validation failure even if a top view looks adjacent.
        translate([2.50, -6.05, 0])
            cube([body_right_x - 2.50, 1.25, 1.80]);
        translate([2.50, 4.80, 0])
            cube([body_right_x - 2.50, 1.25, 1.80]);
        translate([body_right_x - wall_thickness, -body_half_y, 0])
            cube([wall_thickness, 2 * body_half_y, body_height]);

        // Small housing stops visible in the bottom view.
        translate([body_left_x, -4.25, 0]) cube([1.20, 1.50, 1.80]);
        translate([body_left_x, 2.75, 0]) cube([1.20, 1.50, 1.80]);

        for (x = post_x)
            // Extend into the base floor so the join is volumetric rather than
            // a coplanar face that a downstream CAD kernel may split.
            translate([x, 0, -post_depth])
                cylinder(r=post_radius, h=post_depth + 0.20);
    }
}

module contacts() {
    union() {
        // Manufacturer PCB land pattern: 4.5 x 2.3 mm terminals.
        for (x = terminal_centers_x)
            translate([x - terminal_width / 2, -terminal_depth / 2, 0.05])
                cube([terminal_width, terminal_depth, terminal_thickness]);

        // Terminal 1 folded spring contact, simplified from top and side views.
        translate([-6.20, -1.55, 0.72]) cube([7.55, 0.55, terminal_thickness]);
        translate([-6.20, 1.00, 0.72]) cube([7.55, 0.55, terminal_thickness]);
        translate([0.80, -1.00, 0.72]) cube([0.55, 2.00, terminal_thickness]);
        // Fold joins the exposed terminal-1 land to both spring rails. The
        // overlap is volumetric so the exported conductor is one solid.
        translate([-6.20, -1.30, 0.20]) cube([0.45, 2.60, 0.75]);
        translate([-3.90, -1.20, 0.70]) cube([0.60, 2.40, 0.70]);
        translate([-3.80, -1.00, 1.15])
            rotate([0, -8, 0]) cube([4.90, 2.00, terminal_thickness]);

        // Terminal 2 retaining/contact leaves along the insertion-side wall.
        translate([6.45, -4.55, 1.05]) cube([1.00, 3.55, terminal_thickness]);
        translate([6.45, 1.00, 1.05]) cube([1.00, 3.55, terminal_thickness]);
        translate([7.10, -1.00, 0.62]) cube([2.00, 2.00, terminal_thickness]);
        // Central fold joins the terminal-2 land, both retaining leaves, and
        // the contact bar into one conductor without approaching terminal 1.
        translate([6.40, -1.30, 0.20]) cube([1.10, 2.60, 1.10]);
    }
}

module selected_model() {
    if (render_part == "housing" || render_part == "all")
        color(housing_color) housing();
    if (render_part == "contacts" || render_part == "all")
        color(gold_color) contacts();
}

if (projection_view == "top")
    projection(cut=false) selected_model();
else if (projection_view == "front")
    projection(cut=false) rotate([90, 0, 0]) selected_model();
else if (projection_view == "side")
    projection(cut=false) rotate([90, 0, 90]) selected_model();
else
    selected_model();
