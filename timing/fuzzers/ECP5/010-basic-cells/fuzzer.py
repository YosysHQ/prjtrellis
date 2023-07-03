import cell_fuzzers


def main():
    cell_fuzzers.build_and_add(["../../../resource/picorv32_large.v", "../../../resource/distributed_ram.v", "../../../resource/nescore.v"])


if __name__ == "__main__":
    main()
