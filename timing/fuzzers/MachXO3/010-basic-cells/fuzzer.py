import cell_fuzzers


def main():
    cell_fuzzers.build_and_add(["../../../resource/picorv32_large.v", "../../../resource/picorv32_large_blockram.v", "../../../resource/distributed_ram.v"], density="6900", family="MachXO3")


if __name__ == "__main__":
    main()
