from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2ROUTE", family="MachXO2", device="LCMXO2-1200HC", ncl="plc2route.ncl", tiles=["R5C10:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()

    span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')

    def nn_filter(net, netnames):
        """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
        left out by Tcl"""
        return net in netnames or nets.machxo2.is_global(net) or span1_re.match(net)

    interconnect.fuzz_interconnect(config=cfg, location=(5, 10),
                                   netname_predicate=nn_filter,
                                   netname_filter_union=True,
                                   enable_span1_fix=True)

if __name__ == "__main__":
    main()
