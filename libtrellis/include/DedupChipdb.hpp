#ifndef DEDUP_CHIPDB_H
#define DEDUP_CHIPDB_H

#include "RoutingGraph.hpp"
#include <map>
#include <unordered_map>
#include <boost/functional/hash.hpp>
#include <cstdint>
#include <memory>

using namespace std;

namespace Trellis {
namespace DDChipDb {
/*
A deduplicated chip database is a database with the following properties, intended to be used in place-and-route flows.

 - All coordinates are relative
 - All wire, bel and arc IDs are sequential starting from zero at a location
 - Locations with identical wire, bel and arc data once converted to relative coordinates are only stored once
 - The database is fully linked: wires contain arcs and bel pins up and downhill, arcs store their up and down wires,
   etc
 */

struct RelId
{
    Location rel;
    int32_t id = -1;
};

inline bool operator<(RelId a, RelId b)
{
    return (a.rel < b.rel) || (a.rel == b.rel && a.id < b.id);
}

inline bool operator==(RelId a, RelId b)
{
    return (a.rel == b.rel) && (a.id == b.id);
}

inline bool operator!=(RelId a, RelId b)
{
    return (a.rel != b.rel) || (a.id != b.id);
}


struct BelPort
{
    RelId bel;
    ident_t pin = -1;
};

inline bool operator==(const BelPort &a, const BelPort &b)
{
    return a.bel == b.bel && a.pin == b.pin;
}

struct BelWire
{
    RelId wire;
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

struct DdArcData
{
    RelId srcWire;
    RelId sinkWire;
    ArcClass cls;
    int32_t delay;
    ident_t tiletype;
};

inline bool operator==(const DdArcData &a, const DdArcData &b)
{
    return a.srcWire == b.srcWire && a.sinkWire == b.sinkWire && a.cls == b.cls && a.delay == b.delay &&
           a.tiletype == b.tiletype;
}

struct WireData
{
    ident_t name;
    set<RelId> arcsDownhill, arcsUphill;
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

typedef pair<uint64_t, uint64_t> checksum_t;

struct LocationData
{
    vector<WireData> wires;
    vector<DdArcData> arcs;
    vector<BelData> bels;

    checksum_t checksum() const;
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
struct hash<Trellis::DDChipDb::RelId>
{
    std::size_t operator()(const Trellis::DDChipDb::RelId &rid) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::Location>()(rid.rel));
        boost::hash_combine(seed, hash<int32_t>()(rid.id));
        return seed;
    }
};

template<>
struct hash<set<Trellis::DDChipDb::RelId>>
{
    std::size_t operator()(const set<Trellis::DDChipDb::RelId> &rids) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &rid : rids)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::RelId>()(rid));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::DDChipDb::RelId>>
{
    std::size_t operator()(const vector<Trellis::DDChipDb::RelId> &rids) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &rid : rids)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::RelId>()(rid));
        return seed;
    }
};


template<>
struct hash<Trellis::DDChipDb::BelPort>
{
    std::size_t operator()(const Trellis::DDChipDb::BelPort &port) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::DDChipDb::RelId>()(port.bel));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(port.pin));
        return seed;
    }
};

template<>
struct hash<Trellis::DDChipDb::BelWire>
{
    std::size_t operator()(const Trellis::DDChipDb::BelWire &port) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::DDChipDb::RelId>()(port.wire));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(port.pin));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(port.dir));
        return seed;
    }
};


template<>
struct hash<vector<Trellis::DDChipDb::BelPort>>
{
    std::size_t operator()(const vector<Trellis::DDChipDb::BelPort> &bps) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &bp : bps)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::BelPort>()(bp));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::DDChipDb::BelWire>>
{
    std::size_t operator()(const vector<Trellis::DDChipDb::BelWire> &bps) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &bp : bps)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::BelWire>()(bp));
        return seed;
    }
};

template<>
struct hash<Trellis::DDChipDb::DdArcData>
{
    std::size_t operator()(const Trellis::DDChipDb::DdArcData &arc) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::DDChipDb::RelId>()(arc.srcWire));
        boost::hash_combine(seed, hash<Trellis::DDChipDb::RelId>()(arc.sinkWire));
        boost::hash_combine(seed, hash<int8_t>()(arc.cls));
        boost::hash_combine(seed, hash<int32_t>()(arc.delay));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(arc.tiletype));
        return seed;
    }
};

template<>
struct hash<Trellis::DDChipDb::WireData>
{
    std::size_t operator()(const Trellis::DDChipDb::WireData &wire) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::ident_t>()(wire.name));
        boost::hash_combine(seed, hash<set<Trellis::DDChipDb::RelId>>()(wire.arcsDownhill));
        boost::hash_combine(seed, hash<set<Trellis::DDChipDb::RelId>>()(wire.arcsUphill));
        boost::hash_combine(seed, hash<vector<Trellis::DDChipDb::BelPort>>()(wire.belPins));
        return seed;
    }
};

template<>
struct hash<Trellis::DDChipDb::BelData>
{
    std::size_t operator()(const Trellis::DDChipDb::BelData &bel) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<Trellis::ident_t>()(bel.name));
        boost::hash_combine(seed, hash<Trellis::ident_t>()(bel.type));
        boost::hash_combine(seed, hash<vector<Trellis::DDChipDb::BelWire>>()(bel.wires));
        boost::hash_combine(seed, hash<int>()(bel.z));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::DDChipDb::BelData>>
{
    std::size_t operator()(const vector<Trellis::DDChipDb::BelData> &vec) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &item : vec)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::BelData>()(item));
        return seed;
    }
};

template<>
struct hash<vector<Trellis::DDChipDb::DdArcData>>
{
    std::size_t operator()(const vector<Trellis::DDChipDb::DdArcData> &vec) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &item : vec)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::DdArcData>()(item));
        return seed;
    }
};


template<>
struct hash<vector<Trellis::DDChipDb::WireData>>
{
    std::size_t operator()(const vector<Trellis::DDChipDb::WireData> &vec) const noexcept
    {
        std::size_t seed = 0;
        for (const auto &item : vec)
            boost::hash_combine(seed, hash<Trellis::DDChipDb::WireData>()(item));
        return seed;
    }
};

template<>
struct hash<Trellis::DDChipDb::checksum_t>
{
    std::size_t operator()(const Trellis::DDChipDb::checksum_t &cs) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<uint64_t>()(cs.first));
        boost::hash_combine(seed, hash<uint64_t>()(cs.second));
        return seed;
    }
};


template<>
struct hash<Trellis::DDChipDb::LocationData>
{
    std::size_t operator()(const Trellis::DDChipDb::LocationData &ld) const noexcept
    {
        std::size_t seed = 0;
        boost::hash_combine(seed, hash<vector<Trellis::DDChipDb::WireData>>()(ld.wires));
        boost::hash_combine(seed, hash<vector<Trellis::DDChipDb::DdArcData>>()(ld.arcs));
        boost::hash_combine(seed, hash<vector<Trellis::DDChipDb::BelData>>()(ld.bels));
        return seed;
    }
};

}

namespace Trellis {
class Chip;
namespace DDChipDb {


struct DedupChipdb : public IdStore
{
    DedupChipdb();

    DedupChipdb(const IdStore &base);

    map<checksum_t, LocationData> locationTypes;
    map<Location, checksum_t> typeAtLocation;

    LocationData get_cs_data(checksum_t id);
};

shared_ptr<DedupChipdb> make_dedup_chipdb(Chip &chip);

}
}

#endif
