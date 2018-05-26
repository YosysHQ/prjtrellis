import pytrellis
import nonrouting
from fuzzconfig import FuzzConfig
import fuzzloops

"""
This fuzzer is ***HORRIBLE***, but the interfaces we have access to mean there is no better option.

CIB interconnect tiles have muxes that allow the connections into special function tiles from the CIB can be driven to
constant 0 or 1, as well as from general routing. But there is no way to specify this directly for the CIB connections
(which are named as LUT inputs [A-D][0-7]). So this horrible hack emerges instead, whereby we trace the CIB->EBR 
interconnect and drive constants on the EBR instead. We can't treat this as just an EBR configuration as it applies to
all CIBs, including those where this would be difficult to fuzz and location-dependant. So there's probably not much 
choice...
"""


# List of all pins to fuzz
fuzz_pins = [
    "JA0", "JA1", "JA2", "JA3", "JA4", "JA5", "JA6", "JA7",
    "JB0", "JB1", "JB2", "JB3", "JB4", "JB5", "JB6", "JB7",
    "JC0", "JC1", "JC2", "JC3", "JC4", "JC5", "JC6", "JC7",
    "JD0", "JD1", "JD2", "JD3", "JD4", "JD5", "JD6", "JD7",
    "JCE0", "JCE1", "JCE2", "JCE3"
]


cfg = FuzzConfig(job="CIBCONST", family="ECP5", device="LFE5U-25F", ncl="empty.ncl", tiles=["CIB_R25C22:CIB_EBR"])


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "cibconst.ncl"

    def per_pin(pin):
        def get_substs(sig, val):
            if val == pin:
                val = "#SIG"
            subs = {"sig": sig, "val": val}
            return subs
        if pin.startswith("JCE"):
            options = [pin, "1"]
        else:
            options = [pin, "0", "1"]
        # Load the EBR database and find the correct signal
        ebrdb = pytrellis.get_tile_bitdata(
            pytrellis.TileLocator(cfg.family, cfg.device, "MIB_EBR0"))
        fconns = ebrdb.get_fixed_conns()
        sig = None
        for conn in fconns:
            if conn.source == pin:
                sig = conn.sink
                break
        assert sig is not None
        # Convert net name to NCL pin name by stripping extraneous content
        if sig[0] == "J":
            sig = sig[1:]
        sig = sig.replace("_EBR", "")
        nonrouting.fuzz_enum_setting(cfg, "CIB.{}MUX".format(pin), options,
                                     lambda x: get_substs(sig=sig, val=x),
                                     empty_bitfile, False)
    fuzzloops.parallel_foreach(fuzz_pins, per_pin)


if __name__ == "__main__":
    main()
