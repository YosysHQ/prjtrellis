from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis

cfg = FuzzConfig(job="PLC2ROUTE", family="ECP5", device="LFE5U-25F", ncl="plc2route.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    interconnect.fuzz_interconnect(config=cfg, location=(19, 33),
                                   netname_predicate=lambda net, netnames: (net in netnames or nets.is_global(net)),
                                   netname_filter_union=True)
    """interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=["R19C33_A0", "R19C33_A1", "R19C33_Q0"],
                                   netname_predicate=lambda net, netnames: (net in netnames or nets.is_global(net)),
                                   netname_filter_union=False)"""


if __name__ == "__main__":
    main()
