#ifndef LIBTRELLIS_ROUTING_GRAPH_H
#define LIBTRELLIS_ROUTING_GRAPH_H

#include <unordered_map>
#include <map>
#include <vector>
#include <string>
#include <set>
using namespace std;

namespace Trellis {
typedef int32_t ident_t;

struct Location {
    int16_t x = -1, y = -1;
    Location() : x(-1), y(-1){};
    Location(int16_t x, int16_t y) : x(x), y(y){};
    Location(const Location &loc) : x(loc.x), y(loc.y){};
    bool operator==(const Location &other) const { return x == other.x && y == other.y; }
    bool operator!=(const Location &other) const { return x != other.x || y == other.y; }
    bool operator<(const Location &other) const { return y < other.y || (y == other.y && x < other.x); }
};

inline Location operator+(const Location &a, const Location &b) { return Location(a.x + b.x, a.y + b.y); }

struct RoutingId {
    Location loc;
    ident_t id = -1;
    bool operator==(const RoutingId &other) const { return loc == other.loc && id == other.id; }
    bool operator!=(const RoutingId &other) const { return loc != other.loc || id == other.id; }
    bool operator<(const RoutingId &other) const { return loc < other.loc || (loc == other.loc && id < other.id); }
};

struct RoutingArc
{
    ident_t tiletype = -1;
    RoutingId from;
    RoutingId to;
    bool configurable = false;
};

struct RoutingWire
{
    ident_t id = -1;
    vector<RoutingId> uphill;
    vector<RoutingId> downhill;
};

inline bool operator ==(const RoutingWire &a, const RoutingWire &b) {
    return a.id == b.id;
};

struct RoutingTileLoc
{
    Location loc;
    set<RoutingWire> wires;
    vector<RoutingArc> arcs;
};

class RoutingGraph
{
public:
    ident_t ident(const std::string &str) const;
    std::string to_str(ident_t id) const;
    RoutingId id_at_loc(int16_t x, int16_t y, const std::string &str) const;
    std::map<Location, RoutingTileLoc> tiles;
private:
    mutable std::vector<std::string> identifiers;
    mutable std::unordered_map<std::string, int32_t> str_to_id;
};
}
#endif
