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
    bel.z = z;
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

        graph.add_bel_input(bel, graph.ident("WRE"), x, y, graph.ident(fmt("WRE" << z << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WCK"), x, y, graph.ident(fmt("WCK" << z << "_SLICE")));
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
        graph.add_bel_output(bel, graph.ident("WDO0"), x, y, graph.ident("WDO0C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WDO1"), x, y, graph.ident("WDO1C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WDO2"), x, y, graph.ident("WDO2C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WDO3"), x, y, graph.ident("WDO3C_SLICE"));

        graph.add_bel_output(bel, graph.ident("WADO0"), x, y, graph.ident("WADO0C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WADO1"), x, y, graph.ident("WADO1C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WADO2"), x, y, graph.ident("WADO2C_SLICE"));
        graph.add_bel_output(bel, graph.ident("WADO3"), x, y, graph.ident("WADO3C_SLICE"));
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
    bel.z = z;

    graph.add_bel_input(bel, graph.ident("I"), x, y, graph.ident(fmt("PADDO" << l << "_PIO")));
    graph.add_bel_input(bel, graph.ident("T"), x, y, graph.ident(fmt("PADDT" << l << "_PIO")));
    graph.add_bel_output(bel, graph.ident("O"), x, y, graph.ident(fmt("JPADDI" << l << "_PIO")));

    graph.add_bel(bel);
}

void add_dcc(RoutingGraph &graph, int x, int y, string side, string z) {
    string name = side + string("DCC") + z;
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("DCCA");
    bel.loc.x = x;
    bel.loc.y = y;
    if (z == "BL")
        bel.z = 0;
    else if (z == "BR")
        bel.z = 1;
    else if (z == "TL")
        bel.z = 2;
    else if (z == "TR")
        bel.z = 3;
    else
        bel.z = stoi(z);
    graph.add_bel_input(bel, graph.ident("CLKI"), 0, 0, graph.ident(fmt("G_CLKI_" << side << "DCC" << z)));
    graph.add_bel_input(bel, graph.ident("CE"), 0, 0, graph.ident(fmt("G_JCE_" << side << "DCC" << z)));
    graph.add_bel_output(bel, graph.ident("CLKO"), 0, 0, graph.ident(fmt("G_CLKO_" << side << "DCC" << z)));

    graph.add_bel(bel);

}

void add_bram(RoutingGraph &graph, int x, int y, int z) {
    string name = string("EBR") + std::to_string(z);
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("DP16KD");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z;

    for (int i = 0; i < 14; i++) {
        graph.add_bel_input(bel, graph.ident(fmt("ADA" << i)), x, y, graph.ident(fmt("JADA" << i << "_EBR")));
        graph.add_bel_input(bel, graph.ident(fmt("ADB" << i)), x, y, graph.ident(fmt("JADB" << i << "_EBR")));
    }

    graph.add_bel_input(bel, graph.ident("CEA"), x, y, graph.ident("JCEA_EBR"));
    graph.add_bel_input(bel, graph.ident("CEB"), x, y, graph.ident("JCEB_EBR"));
    graph.add_bel_input(bel, graph.ident("CLKA"), x, y, graph.ident("JCLKA_EBR"));
    graph.add_bel_input(bel, graph.ident("CLKB"), x, y, graph.ident("JCLKB_EBR"));
    graph.add_bel_input(bel, graph.ident("CSA0"), x, y, graph.ident("JCSA0_EBR"));
    graph.add_bel_input(bel, graph.ident("CSA1"), x, y, graph.ident("JCSA1_EBR"));
    graph.add_bel_input(bel, graph.ident("CSA2"), x, y, graph.ident("JCSA2_EBR"));
    graph.add_bel_input(bel, graph.ident("CSB0"), x, y, graph.ident("JCSB0_EBR"));
    graph.add_bel_input(bel, graph.ident("CSB1"), x, y, graph.ident("JCSB1_EBR"));
    graph.add_bel_input(bel, graph.ident("CSB2"), x, y, graph.ident("JCSB2_EBR"));

    for (int i = 0; i < 18; i++) {
        graph.add_bel_input(bel, graph.ident(fmt("DIA" << i)), x, y, graph.ident(fmt("JDIA" << i << "_EBR")));
        graph.add_bel_input(bel, graph.ident(fmt("DIB" << i)), x, y, graph.ident(fmt("JDIB" << i << "_EBR")));
        graph.add_bel_output(bel, graph.ident(fmt("DOA" << i)), x, y, graph.ident(fmt("JDOA" << i << "_EBR")));
        graph.add_bel_output(bel, graph.ident(fmt("DOB" << i)), x, y, graph.ident(fmt("JDOB" << i << "_EBR")));
    }


    graph.add_bel_input(bel, graph.ident("OCEA"), x, y, graph.ident("JOCEA_EBR"));
    graph.add_bel_input(bel, graph.ident("OCEB"), x, y, graph.ident("JOCEB_EBR"));
    graph.add_bel_input(bel, graph.ident("RSTA"), x, y, graph.ident("JRSTA_EBR"));
    graph.add_bel_input(bel, graph.ident("RSTB"), x, y, graph.ident("JRSTB_EBR"));
    graph.add_bel_input(bel, graph.ident("WEA"), x, y, graph.ident("JWEA_EBR"));
    graph.add_bel_input(bel, graph.ident("WEB"), x, y, graph.ident("JWEB_EBR"));

    graph.add_bel(bel);

}

}
}
