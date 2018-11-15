from collections import defaultdict

from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re


def mk_numbered_nets(net_list, range_iter):
    return [n.format(i) for i in range_iter for n in net_list]

# Some inputs to the center MUX are two nets concatenated together; the "first"
# net is a sink from locations throughout the FPGA, the "second" is the actual
# input to the center MUX. They should all become fixed connections, but
# fuzz _just_ in case.
def get_first_concat_nets_input():
    nets_01 = mk_numbered_nets(["R6C13_JPCLKCIBLLQ{0}",
                                "R6C13_JPCLKCIBLRQ{0}",
                                "R6C13_JPCLKCIBVIQB{0}",
                                "R6C13_JECLKCIBB{0}",
                                "R6C13_JECLKCIBT{0}",
                                "R6C13_JPCLKCIBVIQT{0}"], range(2))
    nets_23 = mk_numbered_nets(["R6C13_JPCLKCIBMID{0}"], range(2,4))
    return nets_01 + nets_23

# Required to indicate fixed connections in the database.
def get_input_nets():
    # The "second" net of the concatenated inputs.
    def get_second_concat_nets_input():
        nets_01 = mk_numbered_nets(["R6C13_PCLKCIBLLQ{0}",
                                    "R6C13_PCLKCIBLRQ{0}",
                                    "R6C13_PCLKCIBVIQB{0}",
                                    "R6C13_ECLKCIBB{0}",
                                    "R6C13_ECLKCIBT{0}",
                                    "R6C13_PCLKCIBVIQT{0}"], range(2))
        nets_23 = mk_numbered_nets(["R6C13_PCLKCIBMID{0}"], range(2,4))
        return nets_01 + nets_23

    # All other inputs
    nets_07 = mk_numbered_nets(["R6C13_JSNETCIBMID{0}"], range(8))
    nets_01 = mk_numbered_nets(["R6C13_JSNETCIBL{0}",
                                "R6C13_JPCLKT2{0}",
                                "R6C13_JBCDIVX{0}",
                                "R6C13_JBCDIV1{0}",
                                "R6C13_JTCDIVX{0}",
                                "R6C13_JTCDIV1{0}",
                                "R6C13_JPCLKT0{0}",
                                "R6C13_JSNETCIBT{0}",
                                "R6C13_JSNETCIBR{0}",
                                "R6C13_JSNETCIBB{0}"], range(2))
    nets_03 = mk_numbered_nets(["R6C13_JLPLLCLK{0}"], range(4))
    nets_02 = mk_numbered_nets(["R6C13_JPCLKT3{0}"], range(3))
    nets_0 = ["R6C13_JPCLKT10"]

    return get_second_concat_nets_input() + nets_07 + nets_01 + nets_03 + nets_02 + nets_0

# Unfortunately, same deal w/ concatenated nets also applies to the output.
# "second" is kinda a misnomer here- clock nets go through tristates, although
# TCL claims a fixed connection. There are multiple layers of fixed connections
# where the net names change on the outputs, so we just take care of all
# suspected fixed connections in one fell swoop.
def get_fixed_nets_output():
    nets_01 = mk_numbered_nets(["R6C13_CLK{0}_6_DCM",
                                "R6C13_CLK{0}_7_DCM",
                                "R6C13_CLK{0}_1_ECLKBRIDGECS",
                                "R6C13_CLK{0}_0_ECLKBRIDGECS",
                                "R6C13_JSEL{0}_ECLKBRIDGECS"], range(2))
    nets_07 = mk_numbered_nets(["R6C13_CLKI{0}_DCC",
                                # "R6C13_CLKO{0}_DCC", # XXX: I suspect these
                                # are gated by a tristate or a mux.
                                "R6C13_JCE{0}_DCC"], range(8))
    nets_67 = mk_numbered_nets(["R6C13_JSEL{0}_DCM"], range(6,8))
    return nets_01 + nets_07 + nets_67


cfg = FuzzConfig(job="CIB_1200", family="MachXO2", device="LCMXO2-1200HC", ncl="center-ebr-cib_1200.ncl",
                  tiles=["CENTER6:CENTER_EBR_CIB", "CENTER8:CENTER7", "CENTER9:CENTER8"])

def main():
    pytrellis.load_database("../../../database")
    cfg.setup()

    # TODO: Add fc_prefix=job["prefix"] argument.

    interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=get_first_concat_nets_input(),
                                                 netname_filter_union=False,
                                                 netdir_override=defaultdict(lambda : str("sink")),
                                                 full_mux_style=True,
                                                 bias=1)

    interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=get_input_nets(),
                                                 netname_filter_union=False,
                                                 netdir_override=defaultdict(lambda : str("sink")),
                                                 full_mux_style=True,
                                                 bias=1)

    interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=get_fixed_nets_output(),
                                                 netname_filter_union=False,
                                                 netdir_override=defaultdict(lambda : str("sink")),
                                                 full_mux_style=True,
                                                 bias=1)

    # Test fuzzers follow below.
    # interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=["R6C13_PCLKCIBVIQT0", "R6C13_JPCLKCIBVIQT0", "R6C13_VPRXCLKI0", "R6C13_CLKI0_DCC"],
    #                                              netname_filter_union=False,
    #                                              netdir_override = {
    #                                                 "R6C13_JPCLKCIBVIQT0" : "sink",
    #                                              },
    #                                              full_mux_style=True,
    #                                              bias=1)

    # TODO: R6C13_JA0 --> R6C13_JCE0_DCC. But TCL also claims
    # R6C13_CLKI0_DCC --> R6C13_CLKO0_DCC (pseudo = 1). Contradiction?
    # interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=["R6C13_CLKI0_DCC", "R6C13_CLKO0_DCC", "R6C13_JCE0_DCC"],
    #                                              netname_filter_union=False,
    #                                              netdir_override = {
    #                                                 "R6C13_JCE0_DCC" : "sink",
    #                                              },
    #                                              full_mux_style=True,
    #                                              bias=1)


if __name__ == "__main__":
    main()
