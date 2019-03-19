#include "Bels.hpp"
#include "Util.hpp"
#include "Database.hpp"
#include "BitDatabase.hpp"
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
        bel.z = 0;
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
}