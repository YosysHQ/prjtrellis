#!/usr/bin/env python3

import design
import pytrellis
import database


def make_counter(des, name, size, clock, q):
    sum = None
    carry = None
    for i in range(size):
        slice_name = "{}[{}]".format(name, i)
        so_name = "{}[{}]_sum".format(name, i)
        co_name = "{}[{}]_carry".format(name, i)
        q_name = q[i]
        if i == 0:
            sum_lut = [1, 0] * 8
            carry_lut = [0, 1] * 8
            des.inst_slice(name=slice_name, a0=q_name, a1=q_name, f0=so_name, f1=co_name, clk=clock, q0=q_name,
                              params={
                                  "K0.INIT": sum_lut,
                                  "K1.INIT": carry_lut,
                                  "CEMUX": "1",
                                  "GSR": "DISABLED",
                                  "REG0.REGSET": "RESET"
                              })
        else:
            sum_lut = [1, 0, 0, 1] * 4
            carry_lut = [0, 1, 1, 1] * 4
            last_co = "{}[{}]_carry".format(name, i - 1)
            des.inst_slice(name=slice_name, a0=q_name, a1=q_name, b0=last_co, b1=last_co, f0=so_name, f1=co_name,
                              clk=clock, q0=q_name,
                              params={
                                  "K0.INIT": sum_lut,
                                  "K1.INIT": carry_lut,
                                  "CEMUX": "1",
                                  "GSR": "DISABLED",
                                  "REG0.REGSET": "RESET"
                              })


def make_bus(name, size):
    return ["{}[{}]".format(name, i) for i in range(size)]


def main():
    pytrellis.load_database(database.get_db_root())
    des = design.Design("LFE5U-45F")
    ctr_q = make_bus("Q", 8)
    des.router.bind_net_to_port("clk", "R62C89_JQ5") #random input! check!
    make_counter(des, "ctr", 8, "clk", ctr_q)
    des.make_bitstream("counter.bit")


if __name__ == "__main__":
    main()
