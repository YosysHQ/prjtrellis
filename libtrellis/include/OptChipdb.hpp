#ifndef OPT_CHIPDB_H
#define OPT_CHIPDB_H

#include "RoutingGraph.hpp"
#include <map>
#include <unordered_map>
#include <boost/functional/hash.hpp>
#include <cstdint>
#include <memory>

using namespace std;

namespace Trellis {
namespace OptChipDb {
/*
An optimized chip database is a database with the following properties, intended to be used in place-and-route flows.
 - All wire, bel and arc IDs are sequential starting from zero at a location
 - Sequential IDs means it is possible to store wires, bels, and arcs in vectors instead of maps
 - The database is fully linked: wires contain arcs and bel pins up and downhill, arcs store their up and down wires,
   etc

This database is _not_ deduplicated, meaning global data is still stored directly
in this database and relative coordinates are NOT used!
*/

// Essentially a RoutingId where the operators have an inline hint
// (and hashing).
struct OptId
{
    Location rel;
    int32_t id = -1;
};

inline bool operator<(OptId a, OptId b)
{
    return (a.rel < b.rel) || (a.rel == b.rel && a.id < b.id);
}

inline bool operator==(OptId a, OptId b)
{
    return (a.rel == b.rel) && (a.id == b.id);
}

inline bool operator!=(OptId a, OptId b)
{
    return (a.rel != b.rel) || (a.id != b.id);
}


struct BelPort
{
    OptId bel;
    ident_t pin = -1;
};

inline bool operator==(const BelPort &a, const BelPort &b)
{
    return a.bel == b.bel && a.pin == b.pin;
}

struct BelWire
{
    OptId wire;
    ident_t pin = -1;
    PortDirection dir;
};

inline bool operator==(const BelWire &a, const BelWire &b)
{
    return a.wire == b.wire && a.pin == b.pin && a.dir == b.dir;
}


enum ArcClass : int8_t
{
    ARC_STANDARD = 0,
    ARC_FIXED = 1
};

struct OptArcData
{
    OptId srcWire;
    OptId sinkWire;
    ArcClass cls;
    int32_t delay;
    ident_t tiletype;
};

inline bool operator==(const OptArcData &a, const OptArcData &b)
{
    return a.srcWire == b.srcWire && a.sinkWire == b.sinkWire && a.cls == b.cls && a.delay == b.delay &&
           a.tiletype == b.tiletype;
}

struct WireData
{
    ident_t name;
    set<OptId> arcsDownhill, arcsUphill;
    vector<BelPort> belPins;
};

inline bool operator==(const WireData &a, const WireData &b)
{
    return a.name == b.name && a.arcsDownhill.size() == b.arcsDownhill.size() &&
           equal(a.arcsDownhill.begin(), a.arcsDownhill.end(), b.arcsDownhill.begin())
           && a.arcsUphill.size() == b.arcsUphill.size()
           && equal(a.arcsUphill.begin(), a.arcsUphill.end(), b.arcsUphill.begin())
           && a.belPins.size() == b.belPins.size()
           && equal(a.belPins.begin(), a.belPins.end(), b.belPins.begin());
}

struct BelData
{
    ident_t name, type;
    int z;
    vector<BelWire> wires;
};

inline bool operator==(const BelData &a, const BelData &b)
{
    return a.name == b.name && a.type == b.type && a.z == b.z && a.wires.size() == b.wires.size()
           && equal(a.wires.begin(), a.wires.end(), b.wires.begin());
}


struct LocationData
{
    vector<WireData> wires;
    vector<OptArcData> arcs;
    vector<BelData> bels;
};

inline bool operator==(const LocationData &a, const LocationData &b)
{
    return a.wires.size() == b.wires.size() && equal(a.wires.begin(), a.wires.end(), b.wires.begin()) &&
           a.arcs.size() == b.arcs.size() && equal(a.arcs.begin(), a.arcs.end(), b.arcs.begin())
           && a.bels.size() == b.bels.size() && equal(a.bels.begin(), a.bels.end(), b.bels.begin());

}


}
}

namespace std {
template<>
struct hash<Trellis::OptChipDb::OptId>
{
    std::size_t operator()(const Trellis::OptChipDb::OptId &rid) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::Location>()(rid.rel));
        boost::hash_combine(seed, hash<int32_t>()(rid.id));
        return seed;
    }
};

template<>
struct hash<set<Trellis::OptChipDb::OptId>>
{
    std::size_t operator()(const set<Trellis::OptChipDb::OptId> &rids) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &rid : rids)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::OptId>()(rid));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::OptChipDb::OptId>>
{
    std::size_t operator()(const vector<Trellis::OptChipDb::OptId> &rids) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &rid : rids)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::OptId>()(rid));
        return seed;
    }
};


template<>
struct hash<Trellis::OptChipDb::BelPort>
{
    std::size_t operator()(const Trellis::OptChipDb::BelPort &port) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::OptChipDb::OptId>()(port.bel));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(port.pin));
        return seed;
    }
};

template<>
struct hash<Trellis::OptChipDb::BelWire>
{
    std::size_t operator()(const Trellis::OptChipDb::BelWire &port) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::OptChipDb::OptId>()(port.wire));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(port.pin));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(port.dir));
        return seed;
    }
};


template<>
struct hash<vector<Trellis::OptChipDb::BelPort>>
{
    std::size_t operator()(const vector<Trellis::OptChipDb::BelPort> &bps) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &bp : bps)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::BelPort>()(bp));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::OptChipDb::BelWire>>
{
    std::size_t operator()(const vector<Trellis::OptChipDb::BelWire> &bps) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &bp : bps)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::BelWire>()(bp));
        return seed;
    }
};

template<>
struct hash<Trellis::OptChipDb::OptArcData>
{
    std::size_t operator()(const Trellis::OptChipDb::OptArcData &arc) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::OptChipDb::OptId>()(arc.srcWire));
        boost::hash_combine(seed, hash<Trellis::OptChipDb::OptId>()(arc.sinkWire));
        boost::hash_combine(seed, hash<int8_t>()(arc.cls));
        boost::hash_combine(seed, hash<int32_t>()(arc.delay));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(arc.tiletype));
        return seed;
    }
};

template<>
struct hash<Trellis::OptChipDb::WireData>
{
    std::size_t operator()(const Trellis::OptChipDb::WireData &wire) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::ident_t>()(wire.name));
        boost::hash_combine(seed, hash<set<Trellis::OptChipDb::OptId>>()(wire.arcsDownhill));
        boost::hash_combine(seed, hash<set<Trellis::OptChipDb::OptId>>()(wire.arcsUphill));
        boost::hash_combine(seed, hash<vector<Trellis::OptChipDb::BelPort>>()(wire.belPins));
        return seed;
    }
};

template<>
struct hash<Trellis::OptChipDb::BelData>
{
    std::size_t operator()(const Trellis::OptChipDb::BelData &bel) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::ident_t>()(bel.name));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(bel.type));
        boost::hash_combine(seed, hash<vector<Trellis::OptChipDb::BelWire>>()(bel.wires));
        boost::hash_combine(seed, hash<int>()(bel.z));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::OptChipDb::BelData>>
{
    std::size_t operator()(const vector<Trellis::OptChipDb::BelData> &vec) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &item : vec)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::BelData>()(item));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::OptChipDb::OptArcData>>
{
    std::size_t operator()(const vector<Trellis::OptChipDb::OptArcData> &vec) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &item : vec)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::OptArcData>()(item));
        return seed;
    }
};


template<>
struct hash<vector<Trellis::OptChipDb::WireData>>
{
    std::size_t operator()(const vector<Trellis::OptChipDb::WireData> &vec) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &item : vec)
            boost::hash_combine(seed, hash<Trellis::OptChipDb::WireData>()(item));
        return seed;
    }
};

template<>
struct hash<Trellis::OptChipDb::LocationData>
{
    std::size_t operator()(const Trellis::OptChipDb::LocationData &ld) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<vector<Trellis::OptChipDb::WireData>>()(ld.wires));
        boost::hash_combine(seed, hash<vector<Trellis::OptChipDb::OptArcData>>()(ld.arcs));
        boost::hash_combine(seed, hash<vector<Trellis::OptChipDb::BelData>>()(ld.bels));
        return seed;
    }
};

}

namespace Trellis {
class Chip;
namespace OptChipDb {


struct OptChipdb : public IdStore
{
    OptChipdb();

    OptChipdb(const IdStore &base);

    map<Location, LocationData> tiles;
};

shared_ptr<OptChipdb> make_optimized_chipdb(Chip &chip);

}
}

#endif
