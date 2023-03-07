#include "RoutingGraph.hpp"
#include "Chip.hpp"
#include "Tile.hpp"
#include <regex>
#include <iostream>
#include <algorithm>

namespace Trellis {

// This is ignored for the MachXO2 family- globals are handled during routing
// graph creation.
const Location GlobalLoc(-2, -2);

RoutingGraph::RoutingGraph(const Chip &c) : chip_name(c.info.name), chip_family(c.info.family), max_row(c.get_max_row()), max_col(c.get_max_col())
{
    tiles[GlobalLoc].loc = GlobalLoc;
    for (int y = 0; y <= max_row; y++) {
        for (int x = 0; x <= max_col; x++) {
            Location loc(x, y);
            tiles[loc].loc = loc;
        }
    }
    // ECP5
    if (chip_name.find("25F") != string::npos || chip_name.find("12F") != string::npos)
        chip_prefix = "25K_";
    else if (chip_name.find("45F") != string::npos)
        chip_prefix = "45K_";
    else if (chip_name.find("85F") != string::npos)
        chip_prefix = "85K_";
    // MachXO
    else if (chip_name.find("LCMXO256") != string::npos)
        chip_prefix = "256X_";
    else if (chip_name.find("LCMXO640") != string::npos)
        chip_prefix = "640X_";
    else if (chip_name.find("LCMXO1200") != string::npos)
        chip_prefix = "1200X_";
    else if (chip_name.find("LCMXO2280") != string::npos)
        chip_prefix = "2280X_";
    // MachXO2
    else if (chip_name.find("LCMXO2-256") != string::npos)
        chip_prefix = "256_";
    else if (chip_name.find("LCMXO2-640") != string::npos)
        chip_prefix = "640_";
    else if (chip_name.find("LCMXO2-1200") != string::npos)
        chip_prefix = "1200_";
    else if (chip_name.find("LCMXO2-2000") != string::npos)
        chip_prefix = "2000_";
    else if (chip_name.find("LCMXO2-4000") != string::npos)
        chip_prefix = "4000_";
    else if (chip_name.find("LCMXO2-7000") != string::npos)
        chip_prefix = "7000_";
    else
        assert(false);

    if(c.info.family == "MachXO" ||c.info.family == "MachXO2")
        global_data_machxo2 = get_global_info_machxo2(DeviceLocator{c.info.family, c.info.name});
}

ident_t IdStore::ident(const std::string &str) const
{
    if (str_to_id.find(str) != str_to_id.end()) {
        return str_to_id.at(str);
    } else {
        str_to_id[str] = int(identifiers.size());
        identifiers.push_back(str);
        return str_to_id.at(str);
    }
}

std::string IdStore::to_str(ident_t id) const
{
    return identifiers.at(id);
}

RoutingId IdStore::id_at_loc(int16_t x, int16_t y, const std::string &str) const
{
    RoutingId rid;
    rid.id = ident(str);
    rid.loc = Location(x, y);
    return rid;
}

RoutingId RoutingGraph::globalise_net(int row, int col, const std::string &db_name)
{
    if(chip_family == "ECP5") {
        return globalise_net_ecp5(row, col, db_name);
    } else if(chip_family == "MachXO" || chip_family == "MachXO2") {
        return globalise_net_machxo2(row, col, db_name);
    } else
        throw runtime_error("Unknown chip family: " + chip_family);
}

RoutingId RoutingGraph::globalise_net_ecp5(int row, int col, const std::string &db_name)
{
    static const std::regex e(R"(^([NS]\d+)?([EW]\d+)?_(.*))", std::regex::optimize);
    std::string stripped_name = db_name;
    if (db_name.find("25K_") == 0 || db_name.find("45K_") == 0 || db_name.find("85K_") == 0) {
        if (db_name.substr(0, 4) == chip_prefix) {
            stripped_name = db_name.substr(4);
        } else {
            return RoutingId();
        }
    }
    // Workaround for PCSA/B sharing tile dbs
    if (col >= 69) {
        size_t pcsa_pos = stripped_name.find("PCSA");
        if (pcsa_pos != std::string::npos)
            stripped_name.replace(pcsa_pos + 3, 1, "B");
    }
    if (stripped_name.find("G_") == 0 || stripped_name.find("L_") == 0 || stripped_name.find("R_") == 0) {
        // Global net
        // TODO: quadrants and TAP_DRIVE regions
        // TAP_DRIVE and SPINE wires go in their respective tiles
        // Other globals are placed at a nominal location of (0, 0)
        RoutingId id;
        if (stripped_name.find("G_") == 0 && stripped_name.find("VPTX") == string::npos &&
            stripped_name.find("HPBX") == string::npos && stripped_name.find("HPRX") == string::npos) {
            id.loc.x = 0;
            id.loc.y = 0;
        } else {
            id.loc.x = int16_t(col);
            id.loc.y = int16_t(row);
        }
        id.id = ident(stripped_name);
        return id;
    } else {
        RoutingId id;
        id.loc.x = int16_t(col);
        id.loc.y = int16_t(row);
        // Local net, process prefix
        smatch m;
        if (regex_match(stripped_name, m, e)) {
            for (int i = 1; i < int(m.size()) - 1; i++) {
                string g = m.str(i);
                if (g.empty()) continue;
                if (g[0] == 'N') id.loc.y -= std::stoi(g.substr(1));
                else if (g[0] == 'S') id.loc.y += std::stoi(g.substr(1));
                else if (g[0] == 'W') id.loc.x -= std::stoi(g.substr(1));
                else if (g[0] == 'E') id.loc.x += std::stoi(g.substr(1));
                else
                    assert(false);
            }
            id.id = ident(m.str(m.size() - 1));
        } else {
            id.id = ident(stripped_name);
        }
        if (id.loc.x < 0 || id.loc.x > max_col || id.loc.y < 0 || id.loc.y > max_row)
            return RoutingId(); // TODO: handle edge nets properly
        return id;
    }
}

RoutingId RoutingGraph::globalise_net_machxo2(int row, int col, const std::string &db_name)
{
  static const std::regex e(R"(^([NS]\d+)?([EW]\d+)?_(.*))", std::regex::optimize);
  std::string stripped_name = db_name;

  if (db_name.find("256_") == 0 || db_name.find("640_") == 0) {
      if (db_name.substr(0, 4) == chip_prefix) {
          stripped_name = db_name.substr(4);
      } else {
          return RoutingId();
      }
  }

  if (db_name.find("1200_") == 0 || db_name.find("2000_") == 0 ||
      db_name.find("4000_") == 0 || db_name.find("7000_") == 0 ||
      db_name.find("256X_") == 0 || db_name.find("640X_") == 0) {
      if (db_name.substr(0, 5) == chip_prefix) {
          stripped_name = db_name.substr(5);
      } else {
          return RoutingId();
      }
  }

  if (db_name.find("1200X_") == 0 || db_name.find("2280X_") == 0) {
      if (db_name.substr(0, 5) == chip_prefix) {
          stripped_name = db_name.substr(6);
      } else {
          return RoutingId();
      }
  }

  if (stripped_name.find("G_") == 0 || stripped_name.find("L_") == 0 || stripped_name.find("R_") == 0 ||
      stripped_name.find("U_") == 0 || stripped_name.find("D_") == 0 || stripped_name.find("BRANCH_") == 0) {
      // Global prefix detected, use the prefix and row/col to map "logical"
      // globals on a tile basis to physical globals which are shared between
      // tiles.
      return find_machxo2_global_position(row, col, stripped_name);
  } else {
      RoutingId id;
      id.loc.x = int16_t(col);
      id.loc.y = int16_t(row);
      // Local net, process prefix
      smatch m;
      if (regex_match(stripped_name, m, e)) {
          for (int i = 1; i < int(m.size()) - 1; i++) {
              string g = m.str(i);
              if (g.empty()) continue;
              if (g[0] == 'N') id.loc.y -= std::stoi(g.substr(1));
              else if (g[0] == 'S') id.loc.y += std::stoi(g.substr(1));
              else if (g[0] == 'W') {
                  id.loc.x -= std::stoi(g.substr(1));

                  if(id.loc.x < 0) {
                      // Special case: PIO wires on left side have a relative
                      // position placing them outside the chip thanks to MachXO2's
                      // wonderful 1-based column numbering, and lack of dedicated
                      // PIO tiles on the left and right.
                      // Top and bottom unaffected due to dedicated PIO tiles.
                      // TODO: Convert to regex.
                      bool pio_wire = (
                          db_name.find("DI") != string::npos ||
                          db_name.find("JDI") != string::npos ||
                          db_name.find("PADD") != string::npos ||
                          db_name.find("INDD") != string::npos ||
                          db_name.find("IOLDO") != string::npos ||
                          db_name.find("IOLTO") != string::npos ||
                          db_name.find("JCE") != string::npos ||
                          db_name.find("JCLK") != string::npos ||
                          db_name.find("JLSR") != string::npos ||
                          db_name.find("JONEG") != string::npos ||
                          db_name.find("JOPOS") != string::npos ||
                          db_name.find("JTS") != string::npos ||
                          db_name.find("JIN") != string::npos ||
                          db_name.find("JIP") != string::npos ||
                          // Connections to global mux
                          db_name.find("JINCK") != string::npos
                      );

                      if((id.loc.x == -1) && pio_wire)
                          id.loc.x = 0;
                  }
              }
              else if (g[0] == 'E') {
                  id.loc.x += std::stoi(g.substr(1));

                  if(id.loc.x > max_col) {
                      bool pio_wire = (
                          db_name.find("DI") != string::npos ||
                          db_name.find("JDI") != string::npos ||
                          db_name.find("PADD") != string::npos ||
                          db_name.find("INDD") != string::npos ||
                          db_name.find("IOLDO") != string::npos ||
                          db_name.find("IOLTO") != string::npos ||
                          db_name.find("JCE") != string::npos ||
                          db_name.find("JCLK") != string::npos ||
                          db_name.find("JLSR") != string::npos ||
                          db_name.find("JONEG") != string::npos ||
                          db_name.find("JOPOS") != string::npos ||
                          db_name.find("JTS") != string::npos ||
                          db_name.find("JIN") != string::npos ||
                          db_name.find("JIP") != string::npos ||
                          // Connections to global mux
                          db_name.find("JINCK") != string::npos
                      );

                      // Same deal as left side, except the position exceeds
                      // the maximum row.
                      // TODO: Should this become part of general edge-handling
                      // code, rather than a special case in the generic relative-
                      // position logic?
                      if((id.loc.x == max_col + 1) && pio_wire)
                          id.loc.x = max_col;
                  }
              }
              else
                  assert(false);
          }
          id.id = ident(m.str(m.size() - 1));
      } else {
          id.id = ident(stripped_name);
      }
      if (id.loc.x < 0 || id.loc.x > max_col || id.loc.y < 0 || id.loc.y > max_row)
          return RoutingId(); // TODO: handle edge nets properly
      return id;
  }
}

void RoutingGraph::add_arc(Location loc, const RoutingArc &arc)
{
    RoutingId arcId;
    arcId.loc = loc;
    arcId.id = arc.id;
    add_wire(arc.source);
    add_wire(arc.sink);
    tiles[loc].arcs[arc.id] = arc;
    tiles[arc.sink.loc].wires.at(arc.sink.id).uphill.push_back(arcId);
    tiles[arc.source.loc].wires.at(arc.source.id).downhill.push_back(arcId);
}

void RoutingGraph::add_wire(RoutingId wire)
{
    RoutingTileLoc &tile = tiles[wire.loc];
    if (tile.wires.find(wire.id) == tile.wires.end()) {
        RoutingWire rw;
        rw.id = wire.id;
        tiles[wire.loc].wires[rw.id] = rw;
    }
}

void RoutingGraph::add_bel(RoutingBel &bel)
{
    tiles[bel.loc].bels[bel.name] = bel;
}

void RoutingGraph::add_bel_input(RoutingBel &bel, ident_t pin, int wire_x, int wire_y, ident_t wire_name) {
    RoutingId wireId, belId;
    wireId.id = wire_name;
    wireId.loc.x = wire_x;
    wireId.loc.y = wire_y;
    belId.id = bel.name;
    belId.loc = bel.loc;
    add_wire(wireId);
    bel.pins[pin] = make_pair(wireId, PORT_IN);
    tiles[wireId.loc].wires[wireId.id].belsDownhill.push_back(make_pair(belId, pin));
}

void RoutingGraph::add_bel_output(RoutingBel &bel, ident_t pin, int wire_x, int wire_y, ident_t wire_name) {
    RoutingId wireId, belId;
    wireId.id = wire_name;
    wireId.loc.x = wire_x;
    wireId.loc.y = wire_y;
    belId.id = bel.name;
    belId.loc = bel.loc;
    add_wire(wireId);
    bel.pins[pin] = make_pair(wireId, PORT_OUT);
    tiles[wireId.loc].wires[wireId.id].belsUphill.push_back(make_pair(belId, pin));
}

RoutingId RoutingGraph::find_machxo2_global_position(int row, int col, const std::string &db_name) {
    // Globals are given their nominal position, even if they span multiple
    // tiles, by the following rules (determined by a combination of regexes
    // on db_name and row/col):
    smatch m;
    pair<int, int> center = center_map[make_pair(max_row, max_col)];
    RoutingId curr_global;

    GlobalType strategy = get_global_type_from_name(db_name, m);

    // All globals in the center tile get a nominal position of the center
    // tile. We have to use regexes because a number of these connections
    // in the center mux have config bits spread across multiple tiles
    // (although few nets actually have routing bits which cross tiles).
    //
    // This handles L/R_HPSX as well. DCCs are handled a bit differently
    // until we can determine they only truly exist in center tile (the row,
    // col, and db_name will still be enough to distinguish them).
    if(strategy == GlobalType::CENTER) {
        // Some arcs, like those which connect to VPRXCLKI0 in the 1200HC part
        // may appear more than once. We assume that open tools like nextpnr
        // are able to tolerate the same physical arc appearing twice in the
        // routing graph without any problems. This should also make bitstream
        // generation easier if the open tools make sure to set an arc as used
        // in each tile where it exists.
        curr_global.id = ident(db_name);
        curr_global.loc.x = center.second;
        curr_global.loc.y = center.first;
        return curr_global;

    // If we found a global emanating from the CENTER MUX, return a L_/R_
    // global net in the center tile based upon the current tile position
    // (specifically column).
    } else if(strategy == GlobalType::LEFT_RIGHT) {
        assert(row == center.first);
        // Prefixes only required in the center tile.
        assert(db_name[0] == 'G');

        std::string db_copy = db_name;

        // Center column tiles connect to the left side of the center mux.
        if(col <= center.second)
            db_copy[0] = 'L';
        else
            db_copy[0] = 'R';

        curr_global.id = ident(db_copy);
        curr_global.loc.x = center.second;
        curr_global.loc.y = center.first;
        return curr_global;

    // U/D wires get the nominal position of center row, current column.
    // Both U_/D_ and G_ prefixes are handled here.
    } else if(strategy == GlobalType::UP_DOWN) {
        std::string db_copy = db_name;
        std::vector<int> & ud_conns_in_col = global_data_machxo2.ud_conns[col];
        auto conn_begin = ud_conns_in_col.begin();
        auto conn_end = ud_conns_in_col.end();
        int conn_no = std::stoi(m.str(1));

        // First check whether the requested global is in the current column.
        // If not, no point in continuing.
        if(std::find(conn_begin, conn_end, conn_no) == conn_end)
            return RoutingId();

        // Special case the center row, which will have both U/D wires.
        if(row == center.first) {
            assert((db_name[0] == 'U') || (db_name[0] == 'D'));
        } else {
            // Otherwise choose an U_/D_ wire at nominal position based on
            // the current tile's row.
            // Prefixes only required in the center row.
            assert(db_name[0] == 'G');

            // Center column tiles are considered above the center mux,
            // despite sharing the same tile.
            if(row <= center.first)
                db_copy[0] = 'U';
            else
                db_copy[0] = 'D';
        }

        curr_global.id = ident(db_copy);
        curr_global.loc.x = col;
        curr_global.loc.y = center.first;
        return curr_global;

    // BRANCH wires get nominal position of the row/col where they connect
    // to U_/D_ routing. We need the global_data_machxo2 struct to figure
    // out this information.
    } else if(strategy == GlobalType::BRANCH) {
        std::vector<int> candidate_cols;

        if(col > 1)
            candidate_cols.push_back(col - 2);
        if(col > 0)
            candidate_cols.push_back(col - 1);
        candidate_cols.push_back(col);
        if(col < max_col)
            candidate_cols.push_back(col + 1);

        for(auto curr_col : candidate_cols) {
            std::vector<int> & ud_conns_in_col = global_data_machxo2.ud_conns[curr_col];
            auto conn_begin = ud_conns_in_col.begin();
            auto conn_end = ud_conns_in_col.end();
            int conn_no = std::stoi(m.str(1));

            // First check whether the requested global is in the current column.
            // If not, no point in continuing.
            if(std::find(conn_begin, conn_end, conn_no) != conn_end) {
                curr_global.id = ident(db_name);
                curr_global.loc.x = curr_col;
                curr_global.loc.y = row;
                break;
            }
        }

        // One of the candidate columns should have had the correct U/D
        // connection to route to.
        assert(curr_global != RoutingId());
        return curr_global;

    // For OSCH, and DCCs assign nominal position of current requested tile.
    // DCM only exist in center tile but have their routing spread out
    // across tiles.
    } else if(strategy == GlobalType::OTHER) {
        curr_global.id = ident(db_name);
        curr_global.loc.x = col;
        curr_global.loc.y = row;
        return curr_global;
    } else {
        // TODO: Not fuzzed and/or handled yet!
        return RoutingId();
    }
}

RoutingGraph::GlobalType RoutingGraph::get_global_type_from_name(const std::string &db_name, smatch &match) {
    // A RoutingId uniquely describes a net on the chip- using a string
    // identifier (id- converted to int), and a nominal position (loc).
    // Two RoutingIds with the same id and loc represent the same net, so
    // we can use heuristics to connect globals to the rest of the routing
    // graph properly, given the current tile position and the global's
    // identifier.

    // First copy regexes from utils.nets.machxo2, adjusting as necessary for
    // prefixes and regex syntax. Commented-out ones are not ready yet:
    // Globals
    static const std::regex global_entry(R"(G_VPRX(\d){2}00)", std::regex::optimize);
    static const std::regex global_left_right(R"([LR]_HPSX(\d){2}00)", std::regex::optimize);
    static const std::regex global_left_right_g(R"(G_HPSX(\d){2}00)", std::regex::optimize);
    static const std::regex global_up_down(R"([UD]_VPTX(\d){2}00)", std::regex::optimize);
    static const std::regex global_up_down_g(R"(G_VPTX(\d){2}00)", std::regex::optimize);
    static const std::regex global_branch(R"(BRANCH_HPBX(\d){2}00)", std::regex::optimize);

    // High Fanout Secondary Nets
    // static const std::regex hfsn_entry(R"(G_VSRX(\d){2}00)", std::regex::optimize);
    // static const std::regex hfsn_left_right(R"(G_HSSX(\d){2}00)", std::regex::optimize);
    // L2Rs control bidirectional portion of HFSNs!!
    // static const std::regex hfsn_l2r(R"(G_HSSX(\d){2}00_[RL]2[LR])", std::regex::optimize);
    // static const std::regex hfsn_up_down(R"(G_VSTX(\d){2}00)", std::regex::optimize);
    // HSBX(\d){2}00 are fixed connections to HSBX(\d){2}01s.
    // static const std::regex hfsn_branch(R"(G_HSBX(\d){2}0[01])", std::regex::optimize);

    // Center Mux
    // Outputs- entry to DCCs connected to globals (VPRXI -> DCC -> VPRX) *
    static const std::regex center_mux_glb_out(R"(G_VPRXCLKI\d+)", std::regex::optimize);
    // Outputs- connected to ECLKBRIDGEs *
    // static const std::regex center_mux_ebrg_out(R"(G_EBRG(\d){1}CLK(\d){1})", std::regex::optimize);

    // Inputs- CIB routing to HFSNs
    // static const std::regex cib_out_to_hfsn(R"(G_JSNETCIB([TBRL]|MID)(\d){1})", std::regex::optimize);
    // Inputs- CIB routing to globals
    static const std::regex cib_out_to_glb(R"(G_J?PCLKCIB(L[TBRL]Q|MID|VIQ[TBRL])(\d){1})", std::regex::optimize);
    // Inputs- CIB routing to ECLKBRIDGEs
    // static const std::regex cib_out_to_eclk(R"(G_J?ECLKCIB[TBRL](\d){1})", std::regex::optimize);

    // Inputs- Edge clocks dividers
    // static const std::regex eclk_out(R"(G_J?[TBRL]CDIV(X(\d){1}|(\d){2}))", std::regex::optimize);
    // Inputs- PLL
    // static const std::regex pll_out(R"(G_J?[LR]PLLCLK\d+)", std::regex::optimize);
    // Inputs- Clock pads
    // static const std::regex clock_pin(R"(G_J?PCLK[TBLR]\d+)", std::regex::optimize);

    // Part of center-mux but can also be found elsewhere
    // DCCs connected to globals *
    static const std::regex dcc_sig(R"(G_J?(CLK[IO]|CE)(\d){1}[TB]?_DCC)", std::regex::optimize);

    // DCMs- connected to DCCs on globals 6 and 7 *
    static const std::regex dcm_sig(R"(G_J?(CLK(\d){1}_|SEL|DCMOUT)(\d){1}_DCM)", std::regex::optimize);

    // ECLKBRIDGEs- TODO
    // static const std::regex eclkbridge_sig(R"(G_J?(CLK(\d){1}_|SEL|ECSOUT)(\d){1}_ECLKBRIDGECS)", std::regex::optimize);

    // Oscillator output
    static const std::regex osc_clk(R"(G_J?OSC_.*)", std::regex::optimize);

    // Soft Error Detection Clock *
    // static const std::regex sed_clk(R"(G_J?SEDCLKOUT)", std::regex::optimize);

    // PLL/DLL Clocks
    // static const std::regex pll_clk(R"(G_[TB]ECLK\d)", std::regex::optimize);

    // PG/INRD/LVDS
    // static const std::regex pg(R"(G_PG)", std::regex::optimize);
    // static const std::regex inrd(R"(G_INRD)", std::regex::optimize);
    // static const std::regex vds(R"(G_LVDS)", std::regex::optimize);

    // DDR
    // static const std::regex ddrclkpol(R"(G_DDRCLKPOL)", std::regex::optimize);
    // static const std::regex dqsr90(R"(G_DQSR90)", std::regex::optimize);
    // static const std::regex qsw90(R"(G_DQSW90)", std::regex::optimize);

    if(regex_match(db_name, match, global_entry) ||
        regex_match(db_name, match, global_left_right) ||
        regex_match(db_name, match, center_mux_glb_out) ||
        regex_match(db_name, match, cib_out_to_glb) ||
        regex_match(db_name, match, dcm_sig)) {
        return GlobalType::CENTER;
    } else if(regex_match(db_name, match, global_left_right_g)) {
        return GlobalType::LEFT_RIGHT;
    } else if(regex_match(db_name, match, global_up_down) ||
        regex_match(db_name, match, global_up_down_g)) {
        return GlobalType::UP_DOWN;
    } else if(regex_match(db_name, match, global_branch)) {
        return GlobalType::BRANCH;
    } else if(regex_match(db_name, match, dcc_sig) ||
        regex_match(db_name, match, osc_clk)) {
        return GlobalType::OTHER;
    } else {
        // TODO: Not fuzzed and/or handled yet!
        return GlobalType::NONE;
    }
}

}
