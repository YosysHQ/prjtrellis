#ifndef BELS_H
#define BELS_H

#include "Chip.hpp"
#include "RoutingGraph.hpp"

namespace Trellis {
namespace CommonBels {
void add_lc(RoutingGraph &graph, int x, int y, int z);

// Split SLICE Bels
void add_logic_comb(RoutingGraph &graph, int x, int y, int z);
void add_ff(RoutingGraph &graph, int x, int y, int z);
void add_ramw(RoutingGraph &graph, int x, int y);

}

namespace Ecp5Bels {

void add_pio(RoutingGraph &graph, int x, int y, int z);
void add_dcc(RoutingGraph &graph, int x, int y, string side, string z);
void add_dcs(RoutingGraph &graph, int x, int y, int z);
void add_bram(RoutingGraph &graph, int x, int y, int z);
void add_mult18(RoutingGraph &graph, int x, int y, int z);
void add_alu54b(RoutingGraph &graph, int x, int y, int z);
void add_pll(RoutingGraph &graph, std::string quad, int x, int y);
void add_dcu(RoutingGraph &graph, int x, int y);
void add_extref(RoutingGraph &graph, int x, int y);
void add_pcsclkdiv(RoutingGraph &graph, int x, int y, int z);
void add_iologic(RoutingGraph &graph, int x, int y, int z, bool s);
void add_misc(RoutingGraph &graph, const std::string &name, int x, int y);
void add_ioclk_bel(RoutingGraph &graph, const std::string &name, int x, int y, int i, int bank = -1);

}

namespace MachXO2Bels {

void add_pio(RoutingGraph &graph, int x, int y, int z, bool have_dqs);
void add_iologic(RoutingGraph &graph, char side, int x, int y, int z, bool have_dqs, bool have_lvds);
void add_dcc(RoutingGraph &graph, int x, int y, /* const std::string &name, */ int z);
void add_dcm(RoutingGraph &graph, int x, int y, int n, int z);
void add_bram(RoutingGraph &graph, int x, int y);
void add_pll(RoutingGraph &graph, std::string side, int x, int y);
void add_pllrefrc(RoutingGraph &graph, std::string side, int x, int y);
void add_misc(RoutingGraph &graph, const std::string &name, int x, int y);
void add_ioclk_bel(RoutingGraph &graph, const std::string &name, const std::string &side, int x, int y, int i);

}

namespace MachXOBels {

void add_pio(RoutingGraph &graph, int x, int y, int z);

}

}

#endif
