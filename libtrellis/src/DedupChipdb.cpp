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
{}

shared_ptr<DedupChipdb> make_dedup_chipdb(Chip &chip)
{
    shared_ptr<RoutingGraph> graph = chip.get_routing_graph();
    for (auto &loc : graph->tiles) {
        const auto &td = loc.second;
        // Index bels, wires and arcs
        int bel_id = 0, wire_id = 0, arc_id = 0;
        for (auto &bel : td.bels) {
            RoutingId rid;
            rid.loc = loc.first;
            rid.id = bel.first;
            bel.second.cdb_id = bel_id++;
        }
        for (auto &wire : td.wires) {
            RoutingId rid;
            rid.loc = loc.first;
            rid.id = wire.first;
            wire.second.cdb_id  = wire_id++;
        }
        for (auto &arc : td.arcs) {
            RoutingId rid;
            rid.loc = loc.first;
            rid.id = arc.first;
            arc.second.cdb_id = arc_id++;
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
            bd.z = rb.z;
            for (const auto &wire : rb.pins) {
                BelWire bw;
                bw.pin = wire.first;
                bw.wire = RelId{Location(wire.second.first.loc.x - x, wire.second.first.loc.y - y), graph->tiles.at(wire.second.first.loc).wires.at(wire.second.first.id).cdb_id};
                bw.dir = wire.second.second;
                bd.wires.push_back(bw);
            }
            ld.bels.push_back(bd);
        }

        for (const auto &arc : td.arcs) {
            const RoutingArc &ra = arc.second;
            DdArcData ad;
            ad.tiletype = ra.tiletype;
            ad.cls = ra.configurable ? ARC_STANDARD : ARC_FIXED;
            ad.delay = 1;
            ad.sinkWire = RelId{Location(ra.sink.loc.x - x, ra.sink.loc.y - y), graph->tiles.at(ra.sink.loc).wires.at(ra.sink.id).cdb_id};
            ad.srcWire = RelId{Location(ra.source.loc.x - x, ra.source.loc.y - y), graph->tiles.at(ra.source.loc).wires.at(ra.source.id).cdb_id};
            ld.arcs.push_back(ad);
        }

        for (const auto &wire : td.wires) {
            const RoutingWire &rw = wire.second;
            WireData wd;
            wd.name = rw.id;
            for (const auto &dh : rw.downhill)
                wd.arcsDownhill.insert(RelId{Location(dh.loc.x - x, dh.loc.y - y), graph->tiles.at(dh.loc).arcs.at(dh.id).cdb_id});
            for (const auto &uh : rw.uphill)
                wd.arcsUphill.insert(RelId{Location(uh.loc.x - x, uh.loc.y - y), graph->tiles.at(uh.loc).arcs.at(uh.id).cdb_id});
            for (const auto &bdh : rw.belsDownhill) {
                BelPort bp;
                bp.pin = bdh.second;
                bp.bel = RelId{Location(bdh.first.loc.x - x, bdh.first.loc.y - y), graph->tiles.at(bdh.first.loc).bels.at(bdh.first.id).cdb_id};
                wd.belPins.push_back(bp);
            }
            assert(rw.belsUphill.size() <= 1);
            if (rw.belsUphill.size() == 1) {
                const auto &buh = rw.belsUphill[0];
                BelPort uh;
                uh.bel = RelId{Location(buh.first.loc.x - x, buh.first.loc.y - y), graph->tiles.at(buh.first.loc).bels.at(buh.first.id).cdb_id};
                uh.pin = buh.second;
                wd.belPins.push_back(uh);
            }
            ld.wires.push_back(wd);
        }

        checksum_t cs = ld.checksum();
        if (cdb->locationTypes.find(cs) == cdb->locationTypes.end()) {
            cdb->locationTypes[cs] = ld;
        } else {
            if (!(ld == cdb->locationTypes[cs]))
                terminate();
        }
        cdb->typeAtLocation[loc.first] = cs;
    }

    return cdb;
}

LocationData DedupChipdb::get_cs_data(checksum_t id) {
    return locationTypes.at(id);
}

}
}
