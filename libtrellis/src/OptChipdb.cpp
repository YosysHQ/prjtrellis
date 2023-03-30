#include "DedupChipdb.hpp"
#include "Chip.hpp"

#include <iostream>

namespace Trellis {
namespace DDChipDb {

OptimizedChipdb::OptimizedChipdb()
{

}

OptimizedChipdb::OptimizedChipdb(const IdStore &base) : IdStore(base)
{}

shared_ptr<OptimizedChipdb> make_optimized_chipdb(Chip &chip, bool include_lutperm_pips, bool split_slice_mode)
{
    shared_ptr<RoutingGraph> graph = chip.get_routing_graph(include_lutperm_pips, split_slice_mode);
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
    shared_ptr<OptimizedChipdb> cdb = make_shared<OptimizedChipdb>(IdStore(*graph));
    for (const auto &loc : graph->tiles) {
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
                bw.wire = OptId{wire.second.first.loc, graph->tiles.at(wire.second.first.loc).wires.at(wire.second.first.id).cdb_id};
                bw.dir = wire.second.second;
                bd.wires.push_back(bw);
            }
            ld.bels.push_back(bd);
        }

        for (const auto &arc : td.arcs) {
            const RoutingArc &ra = arc.second;
            OptArcData ad;
            ad.tiletype = ra.tiletype;
            ad.cls = ra.configurable ? ARC_STANDARD : ARC_FIXED;
            ad.delay = 1;
            ad.sinkWire = OptId{ra.sink.loc, graph->tiles.at(ra.sink.loc).wires.at(ra.sink.id).cdb_id};
            ad.srcWire = OptId{ra.source.loc, graph->tiles.at(ra.source.loc).wires.at(ra.source.id).cdb_id};
            ld.arcs.push_back(ad);
        }

        for (const auto &wire : td.wires) {
            const RoutingWire &rw = wire.second;
            WireData wd;
            wd.name = rw.id;
            for (const auto &dh : rw.downhill)
                wd.arcsDownhill.insert(OptId{dh.loc, graph->tiles.at(dh.loc).arcs.at(dh.id).cdb_id});
            for (const auto &uh : rw.uphill)
                wd.arcsUphill.insert(OptId{uh.loc, graph->tiles.at(uh.loc).arcs.at(uh.id).cdb_id});
            for (const auto &bdh : rw.belsDownhill) {
                BelPort bp;
                bp.pin = bdh.second;
                bp.bel = OptId{bdh.first.loc, graph->tiles.at(bdh.first.loc).bels.at(bdh.first.id).cdb_id};
                wd.belPins.push_back(bp);
            }
            if (rw.belsUphill.size() > 1) {
                cerr << cdb->to_str(rw.id) << endl;
                for (auto bel : rw.belsUphill) {
                    cerr << cdb->to_str(bel.first.id) << "/" << cdb->to_str(bel.second) << endl;
                }
            }
            assert(rw.belsUphill.size() <= 1);
            if (rw.belsUphill.size() == 1) {
                const auto &buh = rw.belsUphill[0];
                BelPort uh;
                uh.bel = OptId{buh.first.loc, graph->tiles.at(buh.first.loc).bels.at(buh.first.id).cdb_id};
                uh.pin = buh.second;
                wd.belPins.push_back(uh);
            }
            ld.wires.push_back(wd);
        }

        cdb->tiles[loc.first] = ld;
    }

    return cdb;
}

}
}
