#ifndef DEDUP_CHIPDB_H
#define DEDUP_CHIPDB_H

#include "RoutingGraph.hpp"
#include <map>
#include <unordered_map>
#include <boost/functional/hash.hpp>
#include <cstdint>

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
};

inline bool operator==(RelId a, RelId b)
{
    return (a.rel == b.rel) && (a.id == b.id);
};

inline bool operator!=(RelId a, RelId b)
{
    return (a.rel != b.rel) || (a.id != b.id);
};


struct BelPort
{
    RelId bel;
    ident_t pin = -1;
};

struct BelWire
{
    RelId wire;
    ident_t pin = -1;
};

enum ArcClass : int8_t {
    ARC_STANDARD = 0,
    ARC_FIXED = 1
};

struct ArcData
{
    RelId srcWire;
    RelId sinkWire;
    ArcClass cls;
    int32_t delay;
    ident_t tiletype;
};

struct WireData
{
    ident_t name;
    set<RelId> arcsDownhill, arcsUphill;
    vector<BelPort> belsDownhill;
    BelPort belUphill;
};

struct BelData
{
    ident_t name, type;
    vector<BelWire> wires;
};

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
struct hash<Trellis::DDChipDb::ArcData>
{
    std::size_t operator()(const Trellis::DDChipDb::ArcData &arc) const noexcept
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
        boost::hash_combine(seed, hash<vector<Trellis::DDChipDb::BelPort>>()(wire.belsDownhill));
        boost::hash_combine(seed, hash<Trellis::DDChipDb::BelPort>()(wire.belUphill));
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
        return seed;
    }
};

};

namespace Trellis {
namespace DDChipDb {

}
};

#endif
