#include "DedupChipdb.hpp"
#include "Chip.hpp"

namespace Trellis {
namespace DDChipDb {

checksum_t LocationData::checksum() const
{
    pair<uint64_t, uint64_t> cs = make_pair(0, 0);
    const uint64_t magic1 = 0x9e3779b97f4a7c15ULL;
    const uint64_t magic2 = 0xf476452575661fbeULL;
    for (const auto &wire : wires) {
        cs.first = magic1 + std::hash<WireData>()(wire) + (cs.first << 12UL) + (cs.second >> 2UL);
        cs.second = magic2 + std::hash<WireData>()(wire) + (cs.second << 17UL) + (cs.first >> 1UL);
    }
    for (const auto &bel : bels) {
        cs.first = magic1 + std::hash<BelData>()(bel) + (cs.first << 12UL) + (cs.second >> 2UL);
        cs.second = magic2 + std::hash<BelData>()(bel) + (cs.second << 17UL) + (cs.first >> 1UL);
    }
    for (const auto &arc : arcs) {
        cs.first = magic1 + std::hash<DdArcData>()(arc) + (cs.first << 12UL) + (cs.second >> 2UL);
        cs.second = magic2 + std::hash<DdArcData>()(arc) + (cs.second << 17UL) + (cs.first >> 1UL);
    }
    return cs;
}

DedupChipdb::DedupChipdb()
{

}

DedupChipdb::DedupChipdb(const IdStore &base) : IdStore(base)
{};

shared_ptr<DedupChipdb> make_dedup_chipdb(Chip &chip)
{
    map<RoutingId, int> arc_ids;
    map<RoutingId, int> wire_ids;
    map<RoutingId, int> bel_ids;
    shared_ptr<RoutingGraph> graph = chip.get_routing_graph();
    for (auto loc : graph->tiles) {
        const auto &td = loc.second;
        // Index bels, wires and arcs
        int bel_id = 0, wire_id = 0, arc_id = 0;
        for (auto bel : td.bels) {
            RoutingId rid;
            rid.loc = loc.first;
            rid.id = bel.first;
            bel_ids[rid] = bel_id++;
        }
        for (auto wire : td.wires) {
            RoutingId rid;
            rid.loc = loc.first;
            rid.id = wire.first;
            wire_ids[rid] = wire_id++;
        }
        for (auto arc : td.arcs) {
            RoutingId rid;
            rid.loc = loc.first;
            rid.id = arc.first;
            arc_ids[rid] = arc_id++;
        }
    }
    shared_ptr<DedupChipdb> cdb = make_shared<DedupChipdb>(IdStore(*graph));
    for (const auto &loc : graph->tiles) {
        int x = loc.first.x, y = loc.first.y;
        LocationData ld;
        const auto &td = loc.second;
        for (const auto &bel : td.bels) {
            const RoutingBel &rb = bel.second;
            BelData bd;
            bd.name = rb.name;
            bd.type = rb.type;
            for (const auto &wire : rb.pins) {
                BelWire bw;
                bw.pin = wire.first;
                bw.wire = RelId{Location(wire.second.loc.x - x, wire.second.loc.y - y), wire_ids.at(wire.second)};
            }
            ld.bels.push_back(bd);
        }

        for (const auto &arc : td.arcs) {
            const RoutingArc &ra = arc.second;
            DdArcData ad;
            ad.tiletype = ra.tiletype;
            ad.cls = ra.configurable ? ARC_STANDARD : ARC_FIXED;
            ad.delay = 1;
            ad.sinkWire = RelId{Location(ra.sink.loc.x - x, ra.sink.loc.y - y), wire_ids.at(ra.sink)};
            ad.srcWire = RelId{Location(ra.source.loc.x - x, ra.source.loc.y - y), wire_ids.at(ra.source)};
            ld.arcs.push_back(ad);
        }

        for (const auto &wire : td.wires) {
            const RoutingWire &rw = wire.second;
            WireData wd;
            wd.name = rw.id;
            for (const auto &dh : rw.downhill)
                wd.arcsDownhill.insert(RelId{Location(dh.loc.x - x, dh.loc.y - y), arc_ids.at(dh)});
            for (const auto &uh : rw.uphill)
                wd.arcsUphill.insert(RelId{Location(uh.loc.x - x, uh.loc.y - y), arc_ids.at(uh)});
            for (const auto &bdh : rw.belsDownhill) {
                BelPort bp;
                bp.pin = bdh.second;
                bp.bel = RelId{Location(bdh.first.loc.x - x, bdh.first.loc.y - y), bel_ids.at(bdh.first)};
                wd.belsDownhill.push_back(bp);
            }
            assert(rw.belsUphill.size() <= 1);
            if (rw.belsUphill.size() == 1) {
                const auto &buh = rw.belsUphill[0];
                wd.belUphill.bel = RelId{Location(buh.first.loc.x - x, buh.first.loc.y - y), bel_ids.at(buh.first)};
                wd.belUphill.pin = buh.second;
            } else {
                wd.belUphill.bel = RelId{Location(-1, -1), -1};
                wd.belUphill.pin = -1;
            }
        }

        checksum_t cs = ld.checksum();
        if (cdb->locationTypes.find(cs) == cdb->locationTypes.end()) {
            cdb->locationTypes[cs] = ld;
        }
        cdb->typeAtLocation[loc.first] = cs;
    }

    return cdb;
}

LocationData DedupChipdb::get_cs_data(checksum_t id) {
    return locationTypes.at(id);
}

}
};
