from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

cfg = FuzzConfig(job="CIBROUTE", family="ECP5", device="LFE5U-25F", ncl="cibroute.ncl", tiles=["CIB_R1C16:CIB"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()

    span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')

    def nn_filter(net, netnames):
        """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
        left out by Tcl"""
        return ((net in netnames or span1_re.match(net)) and nets.is_cib(net)) or nets.is_global(net)

    def fc_filter(arc, netnames):
        """ Ignore connections between two general routing nets. These are edge buffers which vary based on location
        and must be excluded from the CIB database.
        """
        return not (nets.general_routing_re.match(arc[0]) and nets.general_routing_re.match(arc[1]))
    interconnect.fuzz_interconnect(config=cfg, location=(1, 16),
                                   netname_predicate=nn_filter,
                                   fc_predicate=fc_filter,
                                   netname_filter_union=True,
                                   enable_span1_fix=True)


if __name__ == "__main__":
    main()
