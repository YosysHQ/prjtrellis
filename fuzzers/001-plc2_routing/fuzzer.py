from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis

cfg = FuzzConfig(job="PLC2ROUTE", family="ECP5", device="LFE5U-25F", ncl="plc2route.ncl", tiles=["PLC2:R19C33"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    interconnect.fuzz_interconnect(config=cfg, location=(19, 33),
                                   netname_predicate=lambda net, netnames: (net in netnames or nets.is_global(net)),
                                   netname_filter_union=False)


if __name__ == "__main__":
    main()
