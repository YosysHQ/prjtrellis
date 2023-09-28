import cell_fuzzers


def include_cell(name, type):
    print("{} = {}".format(name, name.startswith("pin_") and name.endswith("_MGIOL")))
    return name.startswith("pin_") and name.endswith("_MGIOL")


def rewrite_cell(name, type):
    if type.startswith("pin_"):
        return "IOLOGIC:MODE={}".format("".join(type.split("_")[1:-1]))
    else:
        return None


def rewrite_pin(name, celltype, pin):
    if type(pin) is list:
        return list(rewrite_pin(name, celltype, x) for x in pin)
    return pin


def main():
    cell_fuzzers.build_and_add(["pio.v"], inc_cell=include_cell, rw_cell_func=rewrite_cell, rw_pin_func=rewrite_pin, family="MachXO3", density="6900")


if __name__ == "__main__":
    main()
