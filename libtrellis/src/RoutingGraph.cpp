#include "RoutingGraph.hpp"
#include "Chip.hpp"
#include "Tile.hpp"
#include <regex>
#include <iostream>

namespace Trellis {

const Location GlobalLoc(-2, -2);

RoutingGraph::RoutingGraph(const Chip &c) : chip_name(c.info.name), max_row(c.get_max_row()), max_col(c.get_max_col())
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
    else
        assert(false);
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
    static const std::regex e(R"(^([NS]\d+)?([EW]\d+)?_(.*))", std::regex::optimize);
    std::string stripped_name = db_name;
    if (db_name.find("25K_") == 0 || db_name.find("45K_") == 0 || db_name.find("85K_") == 0) {
        if (db_name.substr(0, 4) == chip_prefix) {
            stripped_name = db_name.substr(4);
        } else {
            return RoutingId();
        }
    }
    if (stripped_name.find("BNK_") == 0 || stripped_name.find("DQSG_") == 0) // Not yet implemented
        return RoutingId();
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
    tiles[wireId.loc].wires[wireId.id].belsUphill.push_back(make_pair(belId, pin));
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
    tiles[wireId.loc].wires[wireId.id].belsDownhill.push_back(make_pair(belId, pin));
}

}
