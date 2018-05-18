from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2ROUTE", family="ECP5", device="LFE5U-25F", ncl="plc2route.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()

    span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')

    def nn_filter(net, netnames):
        """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
        left out by Tcl"""
        return net in netnames or nets.is_global(net) or span1_re.match(net)

    interconnect.fuzz_interconnect(config=cfg, location=(19, 33),
                                   netname_predicate=nn_filter,
                                   netname_filter_union=True)


if __name__ == "__main__":
    main()
