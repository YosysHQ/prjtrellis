#include "RoutingGraph.hpp"
#include "Chip.hpp"
#include "Tile.hpp"
#include <regex>
#include <iostream>

namespace Trellis {

const Location GlobalLoc(-2, -2);

RoutingGraph::RoutingGraph(const Chip &c) : chip_name(c.info.name), max_row(c.get_max_col()), max_col(c.get_max_row())
{
    tiles[GlobalLoc].loc = GlobalLoc;
    for (int y = 0; y <= max_row; y++) {
        for (int x = 0; x <= max_col; x++) {
            Location loc(x, y);
            tiles[loc].loc = loc;
        }
    }
};

ident_t RoutingGraph::ident(const std::string &str) const
{
    if (str_to_id.find(str) != str_to_id.end()) {
        return str_to_id.at(str);
    } else {
        str_to_id[str] = int(identifiers.size());
        identifiers.push_back(str);
        return str_to_id.at(str);
    }
}

std::string RoutingGraph::to_str(ident_t id) const
{
    return identifiers.at(id);
}

RoutingId RoutingGraph::id_at_loc(int16_t x, int16_t y, const std::string &str) const
{
    RoutingId rid;
    rid.id = ident(str);
    rid.loc = Location(x, y);
    return rid;
}

RoutingId RoutingGraph::globalise_net(int row, int col, const std::string &db_name)
{
    static const std::regex e(R"(^([NS]\d+)?([EW]\d+)?_(.*))", std::regex::optimize);

    if (db_name.find("BNK_") == 0 || db_name.find("DQSG_") == 0) // Not yet implemented
        return RoutingId();
    if (db_name.find("G_") == 0 || db_name.find("L_") == 0 || db_name.find("R_") == 0) {
        // Global net
        // TODO: quadrants and TAP_DRIVE regions
        RoutingId id;
        id.loc = GlobalLoc;
        id.id = ident(db_name.substr(2));
        return id;
    } else {
        RoutingId id;
        id.loc.x = int16_t(col);
        id.loc.y = int16_t(row);
        // Local net, process prefix
        smatch m;
        if (regex_match(db_name, m, e)) {
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
            id.id = ident(db_name);
        }
        if (id.loc.x < 0 || id.loc.x > max_col || id.loc.y < 0 || id.loc.y >= max_row)
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

}
