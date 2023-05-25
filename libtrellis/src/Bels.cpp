#include "Bels.hpp"
#include "Util.hpp"
#include "Database.hpp"
#include "BitDatabase.hpp"
namespace Trellis {
namespace CommonBels {

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

// For split-SLICE (fine-grain) mode

void add_logic_comb(RoutingGraph &graph, int x, int y, int z) {
    char l = "ABCD"[z/2];
    char i = "01"[z%2];
    string name = string("SLICE") + l + string(".K") + i;
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("TRELLIS_COMB");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z * 4;
    // LUT inputs
    graph.add_bel_input(bel, graph.ident("A"), x, y, graph.ident(fmt("A" << z << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("B"), x, y, graph.ident(fmt("B" << z << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("C"), x, y, graph.ident(fmt("C" << z << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("D"), x, y, graph.ident(fmt("D" << z << "_SLICE")));
    // MUX select input
    graph.add_bel_input(bel, graph.ident("M"), x, y, graph.ident(fmt("M" << z << "_SLICE")));

    // Distributed RAM inputs
    if (z < 4) {
        // Write address 
        graph.add_bel_input(bel, graph.ident("WAD0"), x, y, graph.ident(fmt("WAD0" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WAD1"), x, y, graph.ident(fmt("WAD1" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WAD2"), x, y, graph.ident(fmt("WAD2" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WAD3"), x, y, graph.ident(fmt("WAD3" << l << "_SLICE")));
        // Write data
        graph.add_bel_input(bel, graph.ident("WD"), x, y, graph.ident(fmt("WD" << i << l << "_SLICE")));
        // Write enable and clock
        graph.add_bel_input(bel, graph.ident("WRE"), x, y, graph.ident(fmt("WRE" << (z/2) << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("WCK"), x, y, graph.ident(fmt("WCK" << (z/2) << "_SLICE")));
    }

    // Carry input
    if (z == 0)
        graph.add_bel_input(bel, graph.ident("FCI"), x, y, graph.ident("FCI_SLICE"));
    else if ((z % 2) == 0)
        graph.add_bel_input(bel, graph.ident("FCI"), x, y, graph.ident(fmt("FCI" << l << "_SLICE")));
    else
        graph.add_bel_input(bel, graph.ident("FCI"), x, y, graph.ident(fmt("FCI" << l << "1_SLICE")));

    // LUT output
    graph.add_bel_output(bel, graph.ident("F"), x, y, graph.ident(fmt("F" << z << "_SLICE")));
    if ((z % 2) == 0) {
        // Loopback from F1 side to LUT5 mux 'B' input
        graph.add_bel_input(bel, graph.ident("F1"), x, y, graph.ident(fmt("F" << (z + 1) << "_SLICE")));
        // LUT5 mux output
        graph.add_bel_output(bel, graph.ident("OFX"), x, y, graph.ident(fmt("F5" << l << "_SLICE")));
    } else {
        // LUT[678] mux inputs
        graph.add_bel_input(bel, graph.ident("FXA"), x, y, graph.ident(fmt("FXA" << l << "_SLICE")));
        graph.add_bel_input(bel, graph.ident("FXB"), x, y, graph.ident(fmt("FXB" << l << "_SLICE")));
        // LUT[678] mux outputs
        graph.add_bel_output(bel, graph.ident("OFX"), x, y, graph.ident(fmt("FX" << l << "_SLICE")));
    }

    // Carry output
    if (z == 7)
        graph.add_bel_output(bel, graph.ident("FCO"), x, y, graph.ident("FCO_SLICE"));
    else if ((z % 2) == 1)
        graph.add_bel_output(bel, graph.ident("FCO"), x, y, graph.ident(fmt("FCO" << l << "_SLICE")));
    else
        graph.add_bel_output(bel, graph.ident("FCO"), x, y, graph.ident(fmt("FCI" << l << "1_SLICE")));

    graph.add_bel(bel);
}

void add_ff(RoutingGraph &graph, int x, int y, int z) {
    char l = "ABCD"[z/2];
    char i = "01"[z%2];
    string name = string("SLICE") + l + string(".FF") + i;
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("TRELLIS_FF");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z * 4 + 1;
    // DI from COMB
    graph.add_bel_input(bel, graph.ident("DI"), x, y, graph.ident(fmt("DI" << z << "_SLICE")));
    // DI from fabric
    graph.add_bel_input(bel, graph.ident("M"), x, y, graph.ident(fmt("M" << z << "_SLICE")));

    // Control set
    graph.add_bel_input(bel, graph.ident("CLK"), x, y, graph.ident(fmt("CLK" << (z/2) << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("LSR"), x, y, graph.ident(fmt("LSR" << (z/2) << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("CE"), x, y, graph.ident(fmt("CE" << (z/2) << "_SLICE")));

    // Output
    graph.add_bel_output(bel, graph.ident("Q"), x, y, graph.ident(fmt("Q" << z << "_SLICE")));

    graph.add_bel(bel);
}


void add_ramw(RoutingGraph &graph, int x, int y) {
    string name = string("SLICEC.RAMW");
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("TRELLIS_RAMW");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = 4 * 4 + 2;

    int lc0 = 4;
    int lc1 = 5;

    // Input
    graph.add_bel_input(bel, graph.ident("A0"), x, y, graph.ident(fmt("A" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("B0"), x, y, graph.ident(fmt("B" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("C0"), x, y, graph.ident(fmt("C" << lc0 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("D0"), x, y, graph.ident(fmt("D" << lc0 << "_SLICE")));

    graph.add_bel_input(bel, graph.ident("A1"), x, y, graph.ident(fmt("A" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("B1"), x, y, graph.ident(fmt("B" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("C1"), x, y, graph.ident(fmt("C" << lc1 << "_SLICE")));
    graph.add_bel_input(bel, graph.ident("D1"), x, y, graph.ident(fmt("D" << lc1 << "_SLICE")));

    // Output
    graph.add_bel_output(bel, graph.ident("WDO0"), x, y, graph.ident("WDO0C_SLICE"));
    graph.add_bel_output(bel, graph.ident("WDO1"), x, y, graph.ident("WDO1C_SLICE"));
    graph.add_bel_output(bel, graph.ident("WDO2"), x, y, graph.ident("WDO2C_SLICE"));
    graph.add_bel_output(bel, graph.ident("WDO3"), x, y, graph.ident("WDO3C_SLICE"));

    graph.add_bel_output(bel, graph.ident("WADO0"), x, y, graph.ident("WADO0C_SLICE"));
    graph.add_bel_output(bel, graph.ident("WADO1"), x, y, graph.ident("WADO1C_SLICE"));
    graph.add_bel_output(bel, graph.ident("WADO2"), x, y, graph.ident("WADO2C_SLICE"));
    graph.add_bel_output(bel, graph.ident("WADO3"), x, y, graph.ident("WADO3C_SLICE"));
    graph.add_bel(bel);
}

}

namespace Ecp5Bels {

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

    graph.add_bel_input(bel, graph.ident("IOLDO"), x, y, graph.ident(fmt("IOLDO" << l << "_PIO")));
    graph.add_bel_input(bel, graph.ident("IOLTO"), x, y, graph.ident(fmt("IOLTO" << l << "_PIO")));

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

void add_dcs(RoutingGraph &graph, int x, int y, int z) {
    string name = string("DCS") + std::to_string(z);
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("DCSC");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z + 4;
    graph.add_bel_input(bel, graph.ident("CLK0"), 0, 0, graph.ident(fmt("G_CLK0_" << "DCS" << z)));
    graph.add_bel_input(bel, graph.ident("CLK1"), 0, 0, graph.ident(fmt("G_CLK1_" << "DCS" << z)));
    graph.add_bel_output(bel, graph.ident("DCSOUT"), 0, 0, graph.ident(fmt("G_DCSOUT_" << "DCS" << z)));
    graph.add_bel_input(bel, graph.ident("MODESEL"), 0, 0, graph.ident(fmt("G_JMODESEL_" << "DCS" << z)));
    graph.add_bel_input(bel, graph.ident("SEL0"), 0, 0, graph.ident(fmt("G_JSEL0_" << "DCS" << z)));
    graph.add_bel_input(bel, graph.ident("SEL1"), 0, 0, graph.ident(fmt("G_JSEL1_" << "DCS" << z)));
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

void add_mult18(RoutingGraph &graph, int x, int y, int z) {
    string name = string("MULT18_") + std::to_string(z);
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("MULT18X18D");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z;
    auto add_input = [&](const std::string &pin) {
        graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_MULT18")));
    };
    auto add_output = [&](const std::string &pin) {
        graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_MULT18")));
    };
    for (auto sig : {"CLK", "CE", "RST"})
        for (int i = 0; i < 4; i++)
            add_input(fmt(sig << i));
    for (auto sig : {"SIGNED", "SOURCE"})
        for (auto c : {"A", "B"})
            add_input(fmt(sig << c));
    for (auto port : {"A", "B", "C"})
        for (int i = 0; i < 18; i++)
            add_input(fmt(port << i));
    for (auto port : {"SRIA", "SRIB"})
        for (int i = 0; i < 18; i++)
            add_input(fmt(port << i));
    for (auto port : {"ROA", "ROB", "ROC"})
        for (int i = 0; i < 18; i++)
            add_output(fmt(port << i));
    for (auto port : {"SROA", "SROB"})
        for (int i = 0; i < 18; i++)
            add_output(fmt(port << i));
    for (int i = 0; i < 36; i++)
        add_output(fmt("P" << i));
    add_output("SIGNEDP");
    graph.add_bel(bel);
}

void add_alu54b(RoutingGraph &graph, int x, int y, int z) {
    string name = string("ALU54_") + std::to_string(z);
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("ALU54B");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z;
    auto add_input = [&](const std::string &pin) {
        graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_ALU54")));
    };
    auto add_output = [&](const std::string &pin) {
        graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_ALU54")));
    };
    for (auto sig : {"CLK", "CE", "RST"})
        for (int i = 0; i < 4; i++)
            add_input(fmt(sig << i));
    add_input("SIGNEDIA");
    add_input("SIGNEDIB");
    add_input("SIGNEDCIN");
    for (auto port : {"A", "B", "MA", "MB"})
        for (int i = 0; i < 36; i++)
            add_input(fmt(port << i));
    for (auto port : {"C", "CFB", "CIN"})
        for (int i = 0; i < 54; i++)
            add_input(fmt(port << i));
    for (int i = 0; i < 11; i++)
        add_input(fmt("OP" << i));

    for (auto port : {"R", "CO"})
        for (int i = 0; i < 54; i++)
            add_output(fmt(port << i));
    add_output("EQZ");
    add_output("EQZM");
    add_output("EQOM");
    add_output("EQPAT");
    add_output("EQPATB");
    add_output("OVER");
    add_output("UNDER");
    add_output("OVERUNDER");
    add_output("SIGNEDR");
    graph.add_bel(bel);
}

void add_pll(RoutingGraph &graph, std::string quad, int x, int y) {
    string name = string("EHXPLL_") + (quad);
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("EHXPLLL");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = 0;
    auto add_input = [&](const std::string &pin) {
        graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_PLL")));
    };
    auto add_output = [&](const std::string &pin) {
        graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_PLL")));
    };

    add_input("REFCLK");
    add_input("RST");
    add_input("STDBY");

    add_input("PHASEDIR");
    add_input("PHASELOADREG");
    add_input("PHASESEL0");
    add_input("PHASESEL1");
    add_input("PHASESTEP");
    add_input("PLLWAKESYNC");

    add_input("ENCLKOP");
    add_input("ENCLKOS2");
    add_input("ENCLKOS3");
    add_input("ENCLKOS");

    graph.add_bel_input(bel, graph.ident("CLKI"), x, y, graph.ident("CLKI_PLL"));
    graph.add_bel_input(bel, graph.ident("CLKFB"), x, y, graph.ident("CLKFB_PLL"));
    graph.add_bel_output(bel, graph.ident("CLKINTFB"), x, y, graph.ident("CLKINTFB_PLL"));

    add_output("LOCK");
    add_output("INTLOCK");
    add_output("CLKOP");
    add_output("CLKOS");
    add_output("CLKOS2");
    add_output("CLKOS3");

    graph.add_bel(bel);
}

void add_dcu(RoutingGraph &graph, int x, int y) {
    // Just import from routing db
    auto tdb = get_tile_bitdata(TileLocator{"ECP5", "LFE5UM5G-45F", "DCU0"});
    string name = string("DCU");
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("DCUA");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = 0;

    auto endswith = [](const std::string &net, const std::string &ending) {
        return net.substr(net.size()-ending.size(), ending.size()) == ending;
    };

    auto is_pin = [endswith](const std::string &net) {
        if(!endswith(net, "_DCU"))
            return false;
        char c = net.front();
        return c != 'N' && c != 'E' && c != 'W' && c != 'S';
    };

    auto net_to_pin = [endswith](std::string net) {
        if (endswith(net, "_DCU"))
            net.erase(net.size()-4, 4);
        if (net.front() == 'J')
            net.erase(0, 1);
        return net;
    };

    for (const auto &conn : tdb->get_fixed_conns()) {
        if (is_pin(conn.source))
            graph.add_bel_output(bel, graph.ident(net_to_pin(conn.source)), x, y, graph.ident(conn.source));
        if (is_pin(conn.sink))
            graph.add_bel_input(bel, graph.ident(net_to_pin(conn.sink)), x, y, graph.ident(conn.sink));
    }

    graph.add_bel(bel);
}

void add_extref(RoutingGraph &graph, int x, int y) {
    string name = string("EXTREF");
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("EXTREFB");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = 1;
    graph.add_bel_input(bel, graph.ident("REFCLKP"), x, y, graph.ident("REFCLKP_EXTREF"));
    graph.add_bel_input(bel, graph.ident("REFCLKN"), x, y, graph.ident("REFCLKN_EXTREF"));
    graph.add_bel_output(bel, graph.ident("REFCLKO"), x, y, graph.ident("JREFCLKO_EXTREF"));
    graph.add_bel(bel);
}

void add_pcsclkdiv(RoutingGraph &graph, int x, int y, int z) {
    string name = string("PCSCLKDIV" + std::to_string(z));
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident("PCSCLKDIV");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z;
    graph.add_bel_input(bel, graph.ident("CLKI"), x, y, graph.ident("CLKI_" + name));
    graph.add_bel_input(bel, graph.ident("RST"), x, y, graph.ident("JRST_" + name));
    graph.add_bel_input(bel, graph.ident("SEL0"), x, y, graph.ident("JSEL0_" + name));
    graph.add_bel_input(bel, graph.ident("SEL1"), x, y, graph.ident("JSEL1_" + name));
    graph.add_bel_input(bel, graph.ident("SEL2"), x, y, graph.ident("JSEL2_" + name));
    graph.add_bel_output(bel, graph.ident("CDIV1"), x, y, graph.ident("CDIV1_" + name));
    graph.add_bel_output(bel, graph.ident("CDIVX"), x, y, graph.ident("CDIVX_" + name));
    graph.add_bel(bel);
}

void add_iologic(RoutingGraph &graph, int x, int y, int z, bool s) {
    char l = "ABCD"[z];
    std::string ss = s ? "S" : "";
    string name = ss + string("IOLOGIC") + l;
    RoutingBel bel;
    bel.name = graph.ident(name);
    bel.type = graph.ident(ss + "IOLOGIC");
    bel.loc.x = x;
    bel.loc.y = y;
    bel.z = z + (s ? 2 : 4);

    auto add_input = [&](const std::string &pin, bool j = true) {
        graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << l << "_" << ss << "IOLOGIC")));
    };
    auto add_output = [&](const std::string &pin, bool j = true) {
        graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << l << "_" << ss << "IOLOGIC")));
    };

    add_input("DI", false);
    add_output("IOLDO", false);
    add_output("IOLDOD", false);
    add_input("IOLDOI", false);
    add_output("IOLTO", false);
    add_output("INDD", false);

    add_input("PADDI", false);

    add_input("CLK");
    add_input("CE");
    add_input("LSR");

    add_input("LOADN");
    add_input("MOVE");
    add_input("DIRECTION");

    add_input("TSDATA0");
    add_input("TXDATA0");
    add_input("TXDATA1");

    add_output("RXDATA0");
    add_output("RXDATA1");
    add_output("INFF");
    add_output("CFLAG");

    if (!s) {
        add_input("ECLK", false);

        add_input("TSDATA1");
        add_input("TXDATA2");
        add_input("TXDATA3");
        add_output("RXDATA2");
        add_output("RXDATA3");
        if (z % 2 == 0) {
            add_input("TXDATA4");
            add_input("TXDATA5");
            add_input("TXDATA6");
            add_input("SLIP");
            add_output("RXDATA4");
            add_output("RXDATA5");
            add_output("RXDATA6");
        }

        add_input("DQSR90", false);
        add_input("DQSW270", false);
        add_input("DQSW", false);

        add_input("RDPNTR0", false);
        add_input("RDPNTR1", false);
        add_input("RDPNTR2", false);
        add_input("WRPNTR0", false);
        add_input("WRPNTR1", false);
        add_input("WRPNTR2", false);
    }

    graph.add_bel(bel);
}

void add_misc(RoutingGraph &graph, const std::string &name, int x, int y) {
    std::string postfix;
    RoutingBel bel;

    auto add_input = [&](const std::string &pin, bool j = true) {
        graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << "_" << postfix)));
    };
    auto add_output = [&](const std::string &pin, bool j = true) {
        graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << "_" << postfix)));
    };
    bel.name = graph.ident(name);
    bel.type = graph.ident(name);
    bel.loc.x = x;
    bel.loc.y = y;

    if (name == "GSR") {
        postfix = "GSR";
        bel.z = 0;
        add_input("GSR");
        add_input("CLK");
    } else if (name == "JTAGG") {
        postfix = "JTAG";
        bel.z = 1;
        add_input("TCK");
        add_input("TMS");
        add_input("TDI");
        add_input("JTDO2");
        add_input("JTDO1");
        add_output("TDO");
        add_output("JTDI");
        add_output("JTCK");
        add_output("JRTI2");
        add_output("JRTI1");
        add_output("JSHIFT");
        add_output("JUPDATE");
        add_output("JRSTN");
        add_output("JCE2");
        add_output("JCE1");
    } else if (name == "OSCG") {
        postfix = "OSC";
        bel.z = 2;
        graph.add_bel_output(bel, graph.ident("OSC"), 0, 0, graph.ident("G_JOSC_OSC"));
        add_output("SEDSTDBY", false);
    } else if (name == "SEDGA") {
        postfix = "SED";
        bel.z = 3;
        add_input("SEDENABLE");
        add_input("SEDSTART");
        add_input("SEDFRCERR");
        add_output("SEDDONE");
        add_output("SEDINPROG");
        add_output("SEDERR");
        add_input("SEDSTDBY", false);
    } else if (name == "DTR") {
        postfix = "DTR";
        bel.z = 0;
        add_input("STARTPULSE");
        for (int i = 0; i < 8; i++)
            add_output("DTROUT" + std::to_string(i));
    } else if (name == "USRMCLK") {
        postfix = "CCLK";
        bel.z = 1;
        add_input("PADDO");
        add_input("PADDT");
        add_output("PADDI");
    } else {
        throw runtime_error("unknown Bel " + name);
    }
    graph.add_bel(bel);
}

void add_ioclk_bel(RoutingGraph &graph, const std::string &name, int x, int y, int i, int bank) {
    std::string postfix;
    RoutingBel bel;

    auto add_input = [&](const std::string &pin, bool j = true) {
        graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << "_" << postfix)));
    };
    auto add_output = [&](const std::string &pin, bool j = true) {
        graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << "_" << postfix)));
    };
    bel.type = graph.ident(name);
    bel.loc.x = x;
    bel.loc.y = y;

    if (name == "CLKDIVF") {
        postfix = "CLKDIV" + std::to_string(i);
        bel.name = graph.ident(postfix);
        bel.z = i;
        add_input("CLKI", false);
        add_input("RST");
        add_input("ALIGNWD");
        add_output("CDIVX");
    } else if (name == "ECLKSYNCB") {
        postfix = "ECLKSYNC" + std::to_string(i);
        bel.name = graph.ident(postfix + "_BK" + std::to_string(bank));
        bel.z = 8 + i;
        add_input("ECLKI", false);
        add_input("STOP");
        add_output("ECLKO");
    } else if (name == "TRELLIS_ECLKBUF") {
        bel.z = 10 + i;
        bel.name = graph.ident("ECLKBUF" + std::to_string(i));
        graph.add_bel_input(bel, graph.ident("ECLKI"), x, y, graph.ident(fmt("JECLK" << i)));
        graph.add_bel_output(bel, graph.ident("ECLKO"), 0, 0, graph.ident(fmt("G_BANK" << bank << "ECLK" << i)));
    } else if (name == "ECLKBRIDGECS") {
        postfix = "ECLKBRIDGECS" + std::to_string(i);
        bel.name = graph.ident(postfix);
        bel.z = 14;
        add_input("CLK0");
        add_input("CLK1");
        add_input("SEL");
        add_output("ECSOUT", false);
    } else if (name == "BRGECLKSYNC") {
        postfix = "BRGECLKSYNC" + std::to_string(i);
        bel.name = graph.ident(postfix);
        bel.type = graph.ident("ECLKSYNCB");
        bel.z = 15;
        add_input("ECLKI", false);
        add_input("STOP");
        add_output("ECLKO");
    } else if (name == "DLLDELD") {
        postfix = "DLLDEL";
        bel.name = graph.ident(postfix);
        bel.z = 12;
        add_input("A");
        add_input("DDRDEL", false);
        add_input("LOADN");
        add_input("MOVE");
        add_input("DIRECTION");
        add_output("Z", false);
        add_output("CFLAG");
    } else if (name == "DDRDLL") {
        postfix = "DDRDLL";
        bel.name = graph.ident(postfix);
        bel.z = 0;
        add_input("CLK");
        add_input("RST");
        add_input("UDDCNTLN");
        add_input("FREEZE");
        add_output("DDRDEL", false);
        add_output("LOCK");
        add_output("DIVOSC");
        for (int j = 0; j < 8; j++)
            add_output("DCNTL" + std::to_string(j));
    } else if (name == "DQSBUFM") {
        postfix = "DQS";
        bel.name = graph.ident("DQSBUF");
        bel.z = 8;
        add_input("DQSI");
        add_input("READ1");
        add_input("READ0");
        add_input("READCLKSEL2");
        add_input("READCLKSEL1");
        add_input("READCLKSEL0");
        add_input("DDRDEL", false);
        add_input("ECLK", false);
        add_input("SCLK");
        add_input("RST");
        for (int j = 0; j < 8; j++)
            add_input("DYNDELAY" + std::to_string(j));
        add_input("PAUSE");
        add_input("RDLOADN");
        add_input("RDMOVE");
        add_input("RDDIRECTION");
        add_input("WRLOADN");
        add_input("WRMOVE");
        add_input("WRDIRECTION");
        add_output("DQSR90");
        add_output("DQSW");
        add_output("DQSW270");
        for (int j = 0; j < 3; j++) {
            add_output("RDPNTR" + std::to_string(j), false);
            add_output("WRPNTR" + std::to_string(j), false);
        }
        add_output("DATAVALID");
        add_output("BURSTDET");
        add_output("RDCFLAG");
        add_output("WRCFLAG");
    } else {
        throw runtime_error("unknown Bel " + name);
    }
    graph.add_bel(bel);
}


}

namespace MachXO2Bels {
    void add_pio(RoutingGraph &graph, int x, int y, int z, bool have_lvds, bool is_xo3) {
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

        graph.add_bel_input(bel, graph.ident("IOLDO"), x, y, graph.ident(fmt("IOLDO" << l << "_PIO")));
        graph.add_bel_input(bel, graph.ident("IOLTO"), x, y, graph.ident(fmt("IOLTO" << l << "_PIO")));

        graph.add_bel_input(bel, graph.ident("PG"), x, y, graph.ident(fmt("PG" << l << "_PIO")));
        graph.add_bel_input(bel, graph.ident("INRD"), x, y, graph.ident(fmt("INRD" << l << "_PIO")));
        if (have_lvds)
            graph.add_bel_input(bel, graph.ident("LVDS"), x, y, graph.ident(fmt("LVDS" << l << "_PIO")));

        if (is_xo3) {
            graph.add_bel_input(bel, graph.ident("RESEN"), x, y, graph.ident(fmt("JRESEN" << l << "_PIO")));
            graph.add_bel_input(bel, graph.ident("PULLUPEN"), x, y, graph.ident(fmt("JPULLUPEN" << l << "_PIO")));
            graph.add_bel_input(bel, graph.ident("SLEWRATE"), x, y, graph.ident(fmt("JSLEWRATE" << l << "_PIO")));
        }

        graph.add_bel(bel);
    }

    void add_iologic(RoutingGraph &graph, char side, int x, int y, int z, bool have_dqs, bool have_lvds) {
        char l = "ABCD"[z];
        string prefix = "";
        if (!have_lvds) side = 'L'; // no prefix nor additional fields

        if (side=='T' || side=='B') {
            if (z == 0) prefix = side; // A
            if (z == 2) prefix = fmt(side << "S"); // C
        }
        if (side=='R' && have_dqs) {
            prefix = side;
        }

        string name = prefix + string("IOLOGIC") + l;
        RoutingBel bel;
        bel.name = graph.ident(name);
        bel.type = graph.ident(prefix + "IOLOGIC");
        bel.loc.x = x;
        bel.loc.y = y;
        bel.z = z + 4;

        auto add_input = [&](const std::string &pin, bool j = true) {
            graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << l << "_" << prefix << "IOLOGIC")));
        };
        auto add_output = [&](const std::string &pin, bool j = true) {
            graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << l << "_" << prefix << "IOLOGIC")));
        };

        add_output("IOLDO", false);
        add_output("IOLTO", false);
        add_input("PADDI", false);

        add_output("INDD", false);
        add_input("DI", false);

        if (side=='T' && (z % 2 == 0)) { // A and C
            int to = (z==0) ? 8 : 4;
            for (int i = 0; i < to; i++)
                add_input(fmt("TDX" << i));
        }

        if (side=='B' && (z % 2 == 0)) { // A and C
            for (int i = 0; i < 5; i++)
                add_input(fmt("DEL" << i));
        }

        add_input("ONEG");
        add_input("OPOS");

        add_input("TS");

        add_input("CE");
        add_input("LSR");
        add_input("CLK");
        if (side=='T' && (z % 2 == 0)) { // A and C
            add_input("ECLK", false);
        }
        if (side=='B' && (z % 2 == 0)) { // A and C
            add_input("ECLK", false);
            add_input("SLIP");
        }

        if (side=='R' && have_dqs) {
            add_input("DDRCLKPOL", false);
            add_input("DQSR90", false);
            add_input("DQSW90", false);
        }

        add_output("IN");
        add_output("IP");

        if (side=='B' && (z % 2 == 0)) { // A and C
            for (int i = 0; i < 4; i++)
                add_output(fmt("RXD" << i));
        }
        if (side=='B' && z==0) { // A
            for (int i = 0; i < 8; i++)
                add_output(fmt("RXDA" << i));
        }

        graph.add_bel(bel);
    }

    void add_dcc(RoutingGraph &graph, int x, int y, /* const std::string &name, */ int z) {
        // TODO: All DCCs appear to be in center. Phantom DCCs line the columns
        // for global routing with names of the form DCC_RxCy_{0,1}{T,B}. Hence
        // commented-out name parameter.
        // Diamond acknowledges these BELs, but attempting to use them crashes.
        // See if they indeed do exist.
        string name = string("DCC") + std::to_string(z);
        RoutingBel bel;
        bel.name = graph.ident(name);
        bel.type = graph.ident("DCCA");
        bel.loc.x = x;
        bel.loc.y = y;
        bel.z = z;

        graph.add_bel_input(bel, graph.ident("CLKI"), x, y, graph.ident(fmt("G_CLKI" << z << "_DCC")));
        graph.add_bel_input(bel, graph.ident("CE"), x, y, graph.ident(fmt("G_JCE" << z << "_DCC")));
        graph.add_bel_output(bel, graph.ident("CLKO"), x, y, graph.ident(fmt("G_CLKO" << z << "_DCC")));

        graph.add_bel(bel);
    }

    void add_dcm(RoutingGraph &graph, int x, int y, int n, int z) {
        string name = string("DCM") + std::to_string(n);
        RoutingBel bel;
        bel.name = graph.ident(name);
        bel.type = graph.ident("DCMA");
        bel.loc.x = x;
        bel.loc.y = y;
        bel.z = z;

        graph.add_bel_input(bel, graph.ident("CLK0"), x, y, graph.ident(fmt("G_CLK0_" << n << "_DCM")));
        graph.add_bel_input(bel, graph.ident("CLK1"), x, y, graph.ident(fmt("G_CLK1_" << n << "_DCM")));
        graph.add_bel_input(bel, graph.ident("SEL"), x, y, graph.ident(fmt("G_JSEL" << n << "_DCM")));
        graph.add_bel_output(bel, graph.ident("DCMOUT"), x, y, graph.ident(fmt("G_DCMOUT" << n << "_DCM")));

        graph.add_bel(bel);
    }

    void add_bram(RoutingGraph &graph, int x, int y) {
        string name = "EBR";
        RoutingBel bel;
        bel.name = graph.ident(name);
        bel.type = graph.ident("DP8KC");
        bel.loc.x = x;
        bel.loc.y = y;
        bel.z = 0;

        for (int i = 0; i < 13; i++) {
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

        for (int i = 0; i < 9; i++) {
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

        graph.add_bel_output(bel, graph.ident("AE"), x, y, graph.ident("JAE_EBR"));
        graph.add_bel_output(bel, graph.ident("AF"), x, y, graph.ident("JAF_EBR"));
        graph.add_bel_output(bel, graph.ident("EF"), x, y, graph.ident("JEF_EBR"));
        graph.add_bel_output(bel, graph.ident("FF"), x, y, graph.ident("JFF_EBR"));

        graph.add_bel(bel);

    }

    void add_pll(RoutingGraph &graph, std::string side, int x, int y) {
        string name = side + "PLL";
        RoutingBel bel;
        bel.name = graph.ident(name);
        bel.type = graph.ident("EHXPLLJ");
        bel.loc.x = x;
        bel.loc.y = y;
        bel.z = 0;
        auto add_input = [&](const std::string &pin) {
            graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_PLL")));
        };
        auto add_output = [&](const std::string &pin) {
            graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt("J" << pin << "_PLL")));
        };

        graph.add_bel_input(bel, graph.ident("CLKI"), x, y, graph.ident("CLKI_PLL"));
        graph.add_bel_input(bel, graph.ident("CLKFB"), x, y, graph.ident("CLKFB_PLL"));
        add_input("PHASESEL0");
        add_input("PHASESEL1");
        add_input("PHASEDIR");
        add_input("PHASESTEP");
        add_input("LOADREG");
        add_input("STDBY");
        add_input("PLLWAKESYNC");
        add_input("RST");
        add_input("RESETM");
        add_input("RESETC");
        add_input("RESETD");
        add_input("ENCLKOP");
        add_input("ENCLKOS");
        add_input("ENCLKOS2");
        add_input("ENCLKOS3");
        add_input("PLLCLK");
        add_input("PLLRST");
        add_input("PLLSTB");
        add_input("PLLWE");
        for (int i=0;i<8;i++)
            graph.add_bel_input(bel, graph.ident(fmt("PLLDATI" << i)), x, y, graph.ident(fmt("JPLLDATI" << i << "_PLL")));
        for (int i=0;i<5;i++)
            graph.add_bel_input(bel, graph.ident(fmt("PLLADDR" << i)), x, y, graph.ident(fmt("JPLLADDR" << i << "_PLL")));

        add_output("CLKOP");
        add_output("CLKOS");
        add_output("CLKOS2");
        add_output("CLKOS3");
        add_output("LOCK");
        add_output("INTLOCK");
        add_output("REFCLK");
        graph.add_bel_output(bel, graph.ident("CLKINTFB"), x, y, graph.ident("CLKINTFB_PLL"));
        add_output("DPHSRC");
        for (int i=0;i<8;i++)
            graph.add_bel_output(bel, graph.ident(fmt("PLLDATO" << i )), x, y, graph.ident(fmt("JPLLDATI" << i << "_PLL")));
        add_output("PLLACK");


        graph.add_bel(bel);
    }

    void add_pllrefrc(RoutingGraph &graph, std::string side, int x, int y)
    {
        RoutingBel bel;
        bel.name = graph.ident(side + string("PLLREFCS"));
        bel.type = graph.ident("PLLREFCS");
        bel.loc.x = x;
        bel.loc.y = y;
        bel.z = 1;
        graph.add_bel_input(bel, graph.ident("CLK0"), x, y, graph.ident("CLK0_PLLREFCS"));
        graph.add_bel_input(bel, graph.ident("CLK1"), x, y, graph.ident("CLK1_PLLREFCS"));
        graph.add_bel_input(bel, graph.ident("SEL"), x, y, graph.ident("JSEL_PLLREFCS"));
        graph.add_bel_output(bel, graph.ident("PLLCSOUT"), x, y, graph.ident("PLLCSOUT_PLLREFCS"));

        graph.add_bel(bel);
    }

    void add_misc(RoutingGraph &graph, const std::string &name, int x, int y) {
        std::string postfix;
        RoutingBel bel;

        auto add_input = [&](const std::string &pin, bool j = true) {
            graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << "_" << postfix)));
        };
        auto add_output = [&](const std::string &pin, bool j = true) {
            graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << "_" << postfix)));
        };
        bel.name = graph.ident(name);
        bel.type = graph.ident(name);
        bel.loc.x = x;
        bel.loc.y = y;

        if (name == "EFB" || name == "EFBB") {
            postfix = "EFB";
            bel.z = 0;
            // Wishbone
            add_output("WBCUFMIRQ");
            add_output("WBACKO");
            for (int i = 0; i < 8; i++) {
                add_output(fmt("WBDATO" << i));
                add_input(fmt("WBDATI" << i));
                add_input(fmt("WBADRI" << i));
            }
                
            add_input("WBWEI");
            add_input("WBSTBI");
            add_input("WBCYCI");
            add_input("WBRSTI");
            add_input("WBCLKI");

            // PCNTR
            add_output("CFGWAKE", false);
            add_output("CFGSTDBY", false);

            // UFM
            add_input("UFMSN");

            // PLL
            for (int i = 0; i < 8; i++) 
                add_output(fmt("PLLDATO"<< i));
            for (int i = 0; i < 2; i++) {
                add_input(fmt("PLL" << i << "ACKI"));
                add_output(fmt("PLL" << i << "STBO"));
                for (int n = 0; n < 8; n++)
                    add_input(fmt("PLL" << i << "DATI" << n));
            }
            for (int i = 0; i < 5; i++)
                add_output(fmt("PLLADRO" << i));
            add_output("PLLWEO");
            add_output("PLLRSTO");
            add_output("PLLCLKO");
            
            // Timer/Counter
            add_output("TCOC");
            add_output("TCINT");
            add_input("TCIC");
            add_input("TCRSTN");
            add_input("TCCLKI");

            // SPI
            add_output("SPIIRQO");
            add_input("SPISCSN");
            add_output("SPICSNEN");
            add_output("SPIMOSIEN");
            add_output("SPIMOSIO");
            add_input("SPIMOSII");
            add_output("SPIMISOEN");
            add_output("SPIMISOO");
            add_input("SPIMISOI");
            add_output("SPISCKEN");
            add_output("SPISCKO");
            add_input("SPISCKI");
            for (int i = 0; i < 8; i++)
                add_output(fmt("SPIMCSN" << i));

            // I2C primary
            add_output("I2C1IRQO");
            add_output("I2C1SDAOEN");
            add_output("I2C1SDAO");
            add_input("I2C1SDAI");
            add_output("I2C1SCLOEN");
            add_output("I2C1SCLO");
            add_input("I2C1SCLI");
            // I2C secondary
            add_output("I2C2IRQO");
            add_output("I2C2SDAOEN");
            add_output("I2C2SDAO");
            add_input("I2C2SDAI");
            add_output("I2C2SCLOEN");
            add_output("I2C2SCLO");
            add_input("I2C2SCLI");

            if (name == "EFBB") {
                add_output("TAMPERDET");
                add_output("TAMPERTYPE0");
                add_output("TAMPERTYPE1");
                add_output("TAMPERSRC0");
                add_output("TAMPERSRC1");
                add_input("TAMPERDETEN");
                add_input("TAMPERLOCKSRC");
                add_input("TAMPERDETCLK");
            }
        } else if (name == "GSR") {
            postfix = "GSR";
            bel.z = 1;
            add_input("GSR");
            add_input("CLK");
        } else if (name == "JTAGF") {
            postfix = "JTAG";
            bel.z = 2;
            add_input("TCK");
            add_input("TMS");
            add_input("TDI");
            add_input("JTDO2");
            add_input("JTDO1");
            add_output("TDO");
            add_output("JTDI");
            add_output("JTCK");
            add_output("JRTI2");
            add_output("JRTI1");
            add_output("JSHIFT");
            add_output("JUPDATE");
            add_output("JRSTN");
            add_output("JCE2");
            add_output("JCE1");
        } else if (name == "OSCH") {
            postfix = "OSC";
            bel.z = 3;
            add_input("STDBY");
            graph.add_bel_output(bel, graph.ident("OSC"), x, y, graph.ident("G_JOSC_OSC"));
            add_output("SEDSTDBY", false);            
        } else if (name == "OSCJ") {
            postfix = "OSC";
            bel.z = 3;
            add_input("STDBY");
            graph.add_bel_output(bel, graph.ident("OSC"), x, y, graph.ident("G_JOSC_OSC"));
            add_output("SEDSTDBY", false);
            graph.add_bel_output(bel, graph.ident("OSCESB"), x, y, graph.ident("G_JOSCESB_OSC"));
        } else if (name == "PCNTR") {
            postfix = "PCNTR";
            bel.z = 4;
            add_input("CLRFLAG");
            add_input("USERSTDBY");
            add_input("USERTIMEOUT");
            add_input("CLK", false);
            add_input("CFGWAKE", false);
            add_input("CFGSTDBY", false);
            add_output("SFLAG");
            add_output("STDBY");
            add_output("STOP");
        } else if (name == "SEDFA") {
            postfix = "SED";
            bel.z = 5;
            add_input("SEDSTDBY", false);
            add_input("SEDENABLE");
            add_input("SEDSTART");
            add_input("SEDFRCERR");
            add_input("SEDEXCLK");
            add_output("SEDERR");
            add_output("SEDDONE");
            add_output("SEDINPROG");
            add_output("AUTODONE");
        } else if (name == "START") {
            postfix = "START";
            bel.z = 6;
            add_input("STARTCLK");
        } else if (name == "TSALL") {
            postfix = "TSALL";
            bel.z = 7;
            add_input("TSALLI");
        } else {
            throw runtime_error("unknown Bel " + name);
        }
        graph.add_bel(bel);
    }

    void add_ioclk_bel(RoutingGraph &graph, const std::string &name, const std::string &side, int x, int y, int i) {
        std::string postfix;
        RoutingBel bel;

        auto add_input = [&](const std::string &pin, bool j = true) {
            graph.add_bel_input(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << postfix)));
        };
        auto add_output = [&](const std::string &pin, bool j = true) {
            graph.add_bel_output(bel, graph.ident(pin), x, y, graph.ident(fmt((j ? "J" : "") << pin << postfix)));
        };
        bel.type = graph.ident(name);
        bel.loc.x = x;
        bel.loc.y = y;

        if (name == "CLKDIVC") {
            postfix = std::to_string(i) + "_CLKDIV";
            bel.name = graph.ident(side + "CLKDIV" + std::to_string(i));
            bel.z = i;
            add_input("CLKI", false);
            add_input("RST");
            add_input("ALIGNWD");
            add_output("CDIV1");
            add_output("CDIVX");
        } else if (name == "CLKFBBUF") {
            postfix = std::to_string(i) + "_CLKFBBUF";
            bel.name = graph.ident("CLKFBBUF" + std::to_string(i));
            bel.z = 2 + i;
            add_input("A");
            add_output("Z", false);
        } else if (name == "ECLKSYNCA") {
            postfix = std::to_string(i) + "_ECLKSYNC";
            bel.name = graph.ident(side + "ECLKSYNC" + std::to_string(i));
            bel.z = i;
            add_input("ECLKI", false);
            add_input("STOP");
            add_output("ECLKO");
        } else if (name == "ECLKBRIDGECS") {
            postfix = std::to_string(i) + "_ECLKBRIDGECS";
            bel.name = graph.ident("ECLKBRIDGECS" + std::to_string(i));
            bel.z = 10 + i;
            add_input("CLK0");
            add_input("CLK1");
            add_input("SEL");
            add_output("ECSOUT");
        } else if (name == "DLLDELC") {
            postfix = std::to_string(i) + "_DLLDEL";
            bel.name = graph.ident(side + "DLLDEL" + std::to_string(i));
            bel.z = 2 + i;
            add_input("CLKI");
            add_input("DQSDEL");
            add_output("CLKO", false);
        } else if (name == "DQSDLLC") {
            postfix = "_DQSDLL";
            bel.name = graph.ident(side + "DQSDLL");
            bel.z = i;
            add_input("CLK", false);
            add_input("RST");
            add_input("UDDCNTLN");
            add_input("FREEZE");
            add_output("LOCK");
            add_output("DQSDEL");
            //graph.add_bel_output(bel, graph.ident("DQSDLLCLK"), x, y, graph.ident("DQSDLLCLK"));
            //graph.add_bel_output(bel, graph.ident("DQSDLLSCLK"), x, y, graph.ident("JDQSDLLSCLK"));
        } else {
            throw runtime_error("unknown Bel " + name);
        }
        graph.add_bel(bel);
    }

}


namespace MachXOBels {
    void add_pio(RoutingGraph &graph, int x, int y, int z) {
        char l = "ABCDEF"[z];
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
}
}
