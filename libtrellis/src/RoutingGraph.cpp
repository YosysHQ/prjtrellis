#include "RoutingGraph.hpp"
#include "Chip.hpp"
#include "Tile.hpp"
#include <regex>
#include <iostream>

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
    if (chip_name.find("25F") != string::npos || chip_name.find("12F") != string::npos)
        chip_prefix = "25K_";
    else if (chip_name.find("45F") != string::npos)
        chip_prefix = "45K_";
    else if (chip_name.find("85F") != string::npos)
        chip_prefix = "85K_";
    else if (chip_name.find("1200HC") != string::npos)
        // FIXME: Prefix to distinguish XO, XO2, and XO3?
        chip_prefix = "1200_";
    else
        assert(false);

    if(c.info.family == "MachXO2")
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
    } else if(chip_family == "MachXO2") {
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
      db_name.find("4000_") == 0 || db_name.find("7000_") == 0) {
      if (db_name.substr(0, 5) == chip_prefix) {
          stripped_name = db_name.substr(5);
      } else {
          return RoutingId();
      }
  }

  if (stripped_name.find("G_") == 0 || stripped_name.find("L_") == 0 || stripped_name.find("R_") == 0 ||
      stripped_name.find("U_") == 0 || stripped_name.find("D_") == 0 || stripped_name.find("BRANCH_") == 0) {
      //size_t sub_idx = 0;

      // if(stripped_name.find("BRANCH_") == 0) {
      //     sub_idx = 7;
      // } else {
      //     sub_idx = 3;
      // }

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
                      bool pio_wire = (db_name.find("PADD") != string::npos ||
                          db_name.find("IOLDO") != string::npos ||
                          db_name.find("IOLTO") != string::npos ||
                          db_name.find("JINCK") != string::npos);

                      if((id.loc.x == -1) && pio_wire)
                          id.loc.x = 0;
                  }
              }
              else if (g[0] == 'E') {
                  id.loc.x += std::stoi(g.substr(1));

                  if(id.loc.x > max_col) {
                      bool pio_wire = (db_name.find("PADD") != string::npos ||
                        db_name.find("IOLDO") != string::npos ||
                        db_name.find("IOLTO") != string::npos||
                        db_name.find("JINCK") != string::npos);

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
    // A RoutingId uniquely describes a net on the chip- using a string
    // identifier (id- converted to int), and a nominal position (loc).
    // Two RoutingIds with the same id and loc represent the same net, so
    // we can use heuristics to connect globals to the rest of the routing
    // graph properly, given the current tile position and the global's
    // identifier.
    // Globals are given their nominal position, even if they span multiple
    // tiles, by the following rules:

    static const std::regex clk_dcc(R"(^G_CLK[IO]\d[TB]_DCC)", std::regex::optimize);
    smatch m;
    pair<int, int> center = center_map[make_pair(max_row, max_col)];
    RoutingId curr_global;

    // All globals in the center tile get a nominal position of the center
    // tile. This handles L/R_HPSX as well.
    if(make_pair(row, col) == center) {
        curr_global.id = ident(db_name);
        curr_global.loc.x = center.second;
        curr_global.loc.y = center.first;
        return curr_global;

    // If we found a global emanating from the CENTER MUX, return a L_/R_
    // global net in the center tile based upon the current tile position
    // (specifically column).
    } else if(db_name.find("HPSX") != string::npos) {
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
    } else if(db_name.find("VPTX") != string::npos) {
        // Special case the center row, which will have both U/D wires.
        if(row == center.first) {
            assert((db_name[0] == 'U') || (db_name[0] == 'D'));

            curr_global.id = ident(db_name);
            curr_global.loc.x = col;
            curr_global.loc.y = center.first;
            return curr_global;
        } else {
            // Otherwise choose an U_/D_ wire at nominal position based on
            // the current tile's row.
            // Prefixes only required in the center row.
            assert(db_name[0] == 'G');

            std::string db_copy = db_name;

            // Center column tiles are considered above the center mux,
            // despite sharing the same tile.
            if(row <= center.first)
                db_copy[0] = 'U';
            else
                db_copy[0] = 'D';

            curr_global.id = ident(db_copy);
            curr_global.loc.x = col;
            curr_global.loc.y = center.first;
            return curr_global;
        }
    } else if(db_name.find("BRANCH") != string::npos) {
        curr_global.id = ident(db_name);
        curr_global.loc.x = -2;
        curr_global.loc.y = -2;
        return curr_global;
    } else if(regex_match(db_name, m, clk_dcc)) {
        curr_global.id = ident(db_name);
        curr_global.loc.x = col;
        curr_global.loc.y = row;
        return curr_global;
    } else {
        // TODO: Not fuzzed yet!
        return RoutingId();
    }
}

}
