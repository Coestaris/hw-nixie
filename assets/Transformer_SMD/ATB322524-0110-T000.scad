/*
TDK ATB322524-0110-T000 generated-envelope model.
Evidence: TDK ATB3225 type datasheet, page 3, ATB322524 shape and
dimensions plus recommended land pattern (2019-02-21).

Coordinate contract: millimetres; footprint origin is the package centre;
+X runs from pins 1/2 toward pins 4/3, +Y runs from pins 2/3 toward pins 1/4,
and Z=0 is the PCB seating plane. Pin 1 is at -X,+Y.

The outer envelope, 0.50 mm end regions, 1.37 mm winding width, and terminal
layout are documented. Winding height, turn count, terminal thickness, core
beam thickness, and pin-mark dimensions are visual assumptions contained
inside the documented envelope; this is not an exact internal construction.
*/

$fa = 5;
$fs = 0.08;
epsilon = 0.01;
render_part = "all";
projection_view = "3d";

body_x = 3.20;
body_y = 2.50;
body_z = 2.40;
end_region_x = 0.50;
winding_y = 1.37;

terminal_x = 0.50;              // documented package end region
terminal_y = (body_y - winding_y) / 2;
terminal_z = 0.12;              // visual assumption
core_beam_z = 0.45;             // visual assumption from drawing proportions
winding_z = 1.25;               // visual assumption within envelope
winding_bottom_z = 0.30;        // visual assumption
winding_turns = 12;             // cosmetic; manufacturer turn count unpublished
winding_fill = 0.72;
mark_radius = 0.16;             // visual orientation mark assumption
mark_depth = 0.025;
mark_x = -0.62;
mark_y = 0.62;

housing_color = [0.10, 0.11, 0.12];
copper_color = [0.72, 0.30, 0.08];
terminal_color = [0.72, 0.74, 0.76];
mark_color = [0.82, 0.84, 0.86];

module housing() {
    difference() {
        union() {
            // Ferrite top beam and two end legs; overlaps make one solid.
            translate([-body_x / 2, -body_y / 2, body_z - core_beam_z])
                cube([body_x, body_y, core_beam_z]);
            for (x = [-body_x / 2, body_x / 2 - end_region_x])
                translate([x, -body_y / 2, terminal_z - epsilon])
                    cube([end_region_x, body_y,
                          body_z - core_beam_z - terminal_z + 2 * epsilon]);
        }
        // Shallow pin-1 mark stays within the documented maximum height.
        translate([mark_x, mark_y, body_z - mark_depth])
            cylinder(r=mark_radius, h=mark_depth + epsilon);
    }
}

module winding_turn(x_center, turn_width) {
    difference() {
        translate([x_center - turn_width / 2,
                   -winding_y / 2,
                   winding_bottom_z])
            cube([turn_width, winding_y, winding_z]);
        translate([x_center - turn_width / 2 - epsilon,
                   -winding_y / 2 + 0.18,
                   winding_bottom_z + 0.18])
            cube([turn_width + 2 * epsilon,
                  winding_y - 0.36,
                  winding_z - 0.36]);
    }
}

module windings() {
    winding_span_x = body_x - 2 * end_region_x;
    pitch = winding_span_x / winding_turns;
    turn_width = pitch * winding_fill;
    for (index = [0 : winding_turns - 1])
        winding_turn(-winding_span_x / 2 + pitch * (index + 0.5), turn_width);
}

module terminals() {
    for (x = [-body_x / 2, body_x / 2 - terminal_x])
        for (y = [-body_y / 2, body_y / 2 - terminal_y])
            translate([x, y, 0]) cube([terminal_x, terminal_y, terminal_z]);
}

module marking() {
    translate([mark_x, mark_y, body_z - mark_depth])
        cylinder(r=mark_radius, h=mark_depth);
}

module selected_model() {
    if (render_part == "housing" || render_part == "all")
        color(housing_color) housing();
    if (render_part == "windings" || render_part == "all")
        color(copper_color) windings();
    if (render_part == "terminals" || render_part == "all")
        color(terminal_color) terminals();
    if (render_part == "marking" || render_part == "all")
        color(mark_color) marking();
}

if (projection_view == "top")
    projection(cut=false) selected_model();
else if (projection_view == "front")
    projection(cut=false) rotate([90, 0, 0]) selected_model();
else if (projection_view == "side")
    projection(cut=false) rotate([90, 0, 90]) selected_model();
else
    selected_model();
