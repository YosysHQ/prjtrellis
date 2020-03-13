import cell_fuzzers

def include_cell(name, type):
    return type.startswith("mult_reg")

def rewrite_cell_pipemode(name, type):
    if type.startswith("mult_reg"):
        return "MULT18X18D:REGS={}".format(type.split("_", 2)[2])
    else:
        return type

def rewrite_pin(name, type, pin):
    # All DSP pins have the same timings
    if not name.startswith("mult_reg"):
        return pin
    if pin[0] in "ABCP" and pin[1:].isdigit():
        return pin[0]
    else:
        return pin


def main():
    cell_fuzzers.build_and_add(["mult_pipemode.v"], inc_cell=include_cell, rw_cell_func=rewrite_cell_pipemode, rw_pin_func=rewrite_pin)

if __name__ == "__main__":
    main()
