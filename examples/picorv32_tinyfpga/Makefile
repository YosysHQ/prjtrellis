firmware.elf: sections.lds firmware.s
	riscv32-unknown-elf-gcc -march=rv32i -Wl,-Bstatic,-T,sections.lds,--strip-debug -ffreestanding -nostdlib -o firmware.elf firmware.s

firmware.hex: firmware.elf
	riscv32-unknown-elf-objcopy -O verilog firmware.elf /dev/stdout > firmware.hex

attosoc_tb.vvp: attosoc_tb.v attosoc.v picorv32.v
	iverilog -s testbench -o $@ $^

attosoc_sim: attosoc_tb.vvp firmware.hex
	vvp -N $<

attosoc.json: io_wrapper.v attosoc.v picorv32.v firmware.hex
	yosys -p "synth_ecp5 -noccu2 -nomux -nodram -json $@" io_wrapper.v attosoc.v picorv32.v

attosoc_out.config: attosoc.json
	nextpnr-ecp5 --json $< --basecfg ../../misc/basecfgs/empty_lfe5um5g-85f.config --textcfg $@ --85k --package CSFBGA285 --seed 4
attosoc.bit: attosoc_out.config
	ecppack $< $@

prog: attosoc.bit
	tinyprog -p $<

.PHONY: attosoc_sim clean prog
.PRECIOUS: attosoc.json attosoc_out.config attosoc.bit
