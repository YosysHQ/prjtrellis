#ifndef LIBTRELLIS_ROUTING_GRAPH_H
#define LIBTRELLIS_ROUTING_GRAPH_H

#include <unordered_map>
#include <map>
#include <vector>
#include <string>
#include <set>
#include <boost/functional/hash.hpp>

using namespace std;

namespace Trellis {
typedef int32_t ident_t;

struct Location
{
    int16_t x = -1, y = -1;

    Location() : x(-1), y(-1)
    {};

    Location(int16_t x, int16_t y) : x(x), y(y)
    {};

    Location(const Location &loc) : x(loc.x), y(loc.y)
    {};

    bool operator==(const Location &other) const
    { return x == other.x && y == other.y; }

    bool operator!=(const Location &other) const
    { return x != other.x || y == other.y; }

    bool operator<(const Location &other) const
    { return y < other.y || (y == other.y && x < other.x); }
};

extern const Location GlobalLoc;

inline Location operator+(const Location &a, const Location &b)
{ return Location(a.x + b.x, a.y + b.y); }

struct RoutingId
{
    Location loc;
    ident_t id = -1;

    bool operator==(const RoutingId &other) const
    { return loc == other.loc && id == other.id; }

    bool operator!=(const RoutingId &other) const
    { return loc != other.loc || id == other.id; }

    bool operator<(const RoutingId &other) const
    { return loc < other.loc || (loc == other.loc && id < other.id); }
};

struct RoutingArc
{
    ident_t id = -1;
    ident_t tiletype = -1;
    RoutingId source;
    RoutingId sink;
    bool configurable = false;
    mutable int cdb_id = 0;
};

struct RoutingWire
{
    ident_t id = -1;
    vector<RoutingId> uphill;
    vector<RoutingId> downhill;
    vector<pair<RoutingId, ident_t>> belsUphill;
    vector<pair<RoutingId, ident_t>> belsDownhill;
    mutable int cdb_id = 0;
};

inline bool operator==(const RoutingWire &a, const RoutingWire &b)
{
    return a.id == b.id;
}

enum PortDirection {
    PORT_IN = 0,
    PORT_OUT = 1,
    PORT_INOUT = 2
};

struct RoutingBel
{
    ident_t name, type;
    Location loc;
    int z;
    map<ident_t, pair<RoutingId, PortDirection>> pins;
    mutable int cdb_id = 0;
};

struct RoutingTileLoc
{
    Location loc;
    map<ident_t, RoutingWire> wires;
    map<ident_t, RoutingArc> arcs;
    map<ident_t, RoutingBel> bels;
};


inline bool operator==(const RoutingArc &a, const RoutingArc &b)
{
    return a.id == b.id;
}

class Chip;

class IdStore
{
public:
    // Core functions
    ident_t ident(const std::string &str) const;

    std::string to_str(ident_t id) const;

    RoutingId id_at_loc(int16_t x, int16_t y, const std::string &str) const;
private:

private:
    mutable std::vector<std::string> identifiers;
    mutable std::unordered_map<std::string, int32_t> str_to_id;
};

class RoutingGraph : public IdStore
{
public:
    explicit RoutingGraph(const Chip &c);

    // Must be set up beforehand
    std::string chip_name;
    std::string chip_prefix;
    int max_row, max_col;

    // Routing tiles
    std::map<Location, RoutingTileLoc> tiles;

    // Obtain the unique, global identifier for a net inside a tile using the database name
    // Returns an empty RoutingId if net is to be ignored
    RoutingId globalise_net(int row, int col, const std::string &db_name);

    // Add an arc to the graph, automatically adding nets and cross-references as appropriate
    void add_arc(Location loc, const RoutingArc &arc);

    // Add a wire to the graph by id (ignoring it if already existing)
    void add_wire(RoutingId wire);

    // Add a Bel to the graph
    void add_bel(RoutingBel &bel);

    // Add a Bel input or output pin
    void add_bel_input(RoutingBel &bel, ident_t pin, int wire_x, int wire_y, ident_t wire_name);
    void add_bel_output(RoutingBel &bel, ident_t pin, int wire_x, int wire_y, ident_t wire_name);
};
}

namespace std {
template <> struct hash <Trellis::Location>
{
    std::size_t operator()(const Trellis::Location &loc) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<int>()(loc.x));
        boost::hash_combine(seed, hash<int>()(loc.y));
        return seed;
    }
};
}


#endif
