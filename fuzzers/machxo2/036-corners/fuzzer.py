from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re
import argparse

jobs = [
        # URC0 has same routing as `CIB_PIC_T`, except for globals.
        {
            "cfg": FuzzConfig(job="URC0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute.ncl", tiles=["PR1:URC0"]),
            "location": (1, 22),
            "nn_filter_extra": []
        },

        # ULC0 appears to have unique routing and globals.
        {
            "cfg": FuzzConfig(job="ULC0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute.ncl", tiles=["PL1:ULC0"]),
            "location": (1, 1),
            "nn_filter_extra": []
        },

        # LLC0 has same routing and globals as PIC_L0.
        {
            "cfg": FuzzConfig(job="LLC0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute.ncl", tiles=["PL11:LLC0"]),
            "location": (11, 1),
            "nn_filter_extra": []
        },

        # LRC0 has same routing and globals as PIC_R0.
        {
            "cfg": FuzzConfig(job="LRC0ROUTE", family="MachXO2", device="LCMXO2-1200HC",
                        ncl="cibroute.ncl", tiles=["PR11:LRC0"]),
            "location": (11, 22),
            "nn_filter_extra": []
        },
]


def main(args):
    pytrellis.load_database("../../../database")
    for job in [jobs[i] for i in args.ids]:
        cfg = job["cfg"]
        cfg.setup()

        span1_re = re.compile(r'R\d+C\d+_[VH]01[NESWTLBR]\d{4}')

        def nn_filter(net, netnames):
            """I want to handle global nets that are associated with this
            tile manually; any matching nets are filtered out."""
            if net in job["nn_filter_extra"]:
                return False

            """ Match nets that are: in the tile according to Tcl, global nets, or span-1 nets that are accidentally
            left out by Tcl"""
            return ((net in netnames or span1_re.match(net)) and nets.is_cib(net)) or nets.machxo2.is_global(net)

        def fc_filter(arc, netnames):
            """ Ignore connections between two general routing nets. These are edge buffers which vary based on location
            and must be excluded from the CIB database.
            """
            return not (nets.general_routing_re.match(arc[0]) and nets.general_routing_re.match(arc[1]))
        interconnect.fuzz_interconnect(config=cfg, location=job["location"],
                                       netname_predicate=nn_filter,
                                       fc_predicate=fc_filter,
                                       netname_filter_union=True,
                                       enable_span1_fix=True,
                                       netdir_override=defaultdict(lambda : str("ignore")))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corner Fuzzer.")
    parser.add_argument(dest="ids", metavar="N", type=int, nargs="*",
                    default=range(0, len(jobs)), help="Job (indices) to run.")
    args = parser.parse_args()
    main(args)
