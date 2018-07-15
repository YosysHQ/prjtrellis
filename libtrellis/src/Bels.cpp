#include "Bels.hpp"
#include "Util.hpp"
namespace Trellis {
namespace Bels {

void add_lc(RoutingGraph &graph, int x, int y, int z) {
    char l = "ABCD"[z];
    string name = string("SLICE") + l;
    int lc0 = z * 2;
    int lc1 = z * 2 + 1;
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("SLICE");
    bel.loc.x = x;
    bel.loc.y = y;
    graph.add_bel_input(bel, graph.ident("A0"), x, y, graph.ident(fmt("A" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("B0"), x, y, graph.ident(fmt("B" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("C0"), x, y, graph.ident(fmt("C" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("D0"), x, y, graph.ident(fmt("D" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("M0"), x, y, graph.ident(fmt("M" << lc0 << "_SLICE")));

    graph.add_bel_input(bel, graph.ident("A1"), x, y, graph.ident(fmt("A" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("B1"), x, y, graph.ident(fmt("B" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("C1"), x, y, graph.ident(fmt("C" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("D1"), x, y, graph.ident(fmt("D" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("M1"), x, y, graph.ident(fmt("M" << lc1 << "_SLICE")));
    if (z == 0)
        graph.add_bel_input(bel, graph.ident("FCI"), x, y, graph.ident("FCI_SLICE"));
    else
        graph.add_bel_input(bel, graph.ident("FCI"), x, y, graph.ident(fmt("FCI" << l << "_SLICE")));

    graph.add_bel_input(bel, graph.ident("FXA"), x, y, graph.ident(fmt("FXA" << l << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("FXB"), x, y, graph.ident(fmt("FXB" << l << "_SLICE")));

    graph.add_bel_input(bel, graph.ident("CLK"), x, y, graph.ident(fmt("CLK" << z << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("LSR"), x, y, graph.ident(fmt("LSR" << z << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("CE"), x, y, graph.ident(fmt("CE" << z << "_SLICE")));

    graph.add_bel_input(bel, graph.ident("DI0"), x, y, graph.ident(fmt("DI" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("DI1"), x, y, graph.ident(fmt("DI" << lc1 << "_SLICE")));

    if (z == 0 || z == 1) {
        graph.add_bel_input(bel, graph.ident("WD0"), x, y, graph.ident(fmt("WD0" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WD1"), x, y, graph.ident(fmt("WD1" << l << "_SLICE")));

        graph.add_bel_input(bel, graph.ident("WAD0"), x, y, graph.ident(fmt("WAD0" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WAD1"), x, y, graph.ident(fmt("WAD1" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WAD2"), x, y, graph.ident(fmt("WAD2" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WAD3"), x, y, graph.ident(fmt("WAD3" << l << "_SLICE")));

        graph.add_bel_input(bel, graph.ident("WRE"), x, y, graph.ident(fmt("WRE" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WCK"), x, y, graph.ident(fmt("WCK" << l << "_SLICE")));
    }

    graph.add_bel_output(bel, graph.ident("F0"), x, y, graph.ident(fmt("F" << lc0 << "_SLICE")));
    graph.add_bel_output(bel, graph.ident("Q0"), x, y, graph.ident(fmt("Q" << lc0 << "_SLICE")));

    graph.add_bel_output(bel, graph.ident("F1"), x, y, graph.ident(fmt("F" << lc1 << "_SLICE")));
    graph.add_bel_output(bel, graph.ident("Q1"), x, y, graph.ident(fmt("Q" << lc1 << "_SLICE")));

    graph.add_bel_output(bel, graph.ident("OFX0"), x, y, graph.ident(fmt("F5" << l << "_SLICE")));
    graph.add_bel_output(bel, graph.ident("OFX1"), x, y, graph.ident(fmt("FX" << l << "_SLICE")));

    if (z == 3)
        graph.add_bel_output(bel, graph.ident("FCO"), x, y, graph.ident("FCO_SLICE"));
    else
        graph.add_bel_output(bel, graph.ident("FCO"), x, y, graph.ident(fmt("FCO" << l << "_SLICE")));

    if (z == 2) {
        graph.add_bel_output(bel, graph.ident("WD0"), x, y, graph.ident("WD0C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WD1"), x, y, graph.ident("WD1C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WD2"), x, y, graph.ident("WD2C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WD3"), x, y, graph.ident("WD3C_SLICE"));

        graph.add_bel_output(bel, graph.ident("WAD0"), x, y, graph.ident("WAD0C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WAD1"), x, y, graph.ident("WAD1C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WAD2"), x, y, graph.ident("WAD2C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WAD3"), x, y, graph.ident("WAD3C_SLICE"));
    }
    graph.add_bel(bel);
}

void add_pio(RoutingGraph &graph, int x, int y, int z) {
    char l = "ABCD"[z];
    string name = string("PIO") + l;
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("PIO");
    bel.loc.x = x;
    bel.loc.y = y;

    graph.add_bel_input(bel, graph.ident("I"), x, y, graph.ident(fmt("PADDO" << l << "_PIO")));
    graph.add_bel_input(bel, graph.ident("T"), x, y, graph.ident(fmt("PADDT" << l << "_PIO")));
    graph.add_bel_output(bel, graph.ident("O"), x, y, graph.ident(fmt("JPADDI" << l << "_PIO")));

    graph.add_bel(bel);
}

}
}
