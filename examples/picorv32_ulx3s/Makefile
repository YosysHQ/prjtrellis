firmware.elf: sections.lds firmware.s
	riscv32-unknown-elf-gcc -march=rv32i -Wl,-Bstatic,-T,sections.lds,--strip-debug -ffreestanding -nostdlib -o firmware.elf firmware.s

firmware.hex: firmware.elf
	riscv32-unknown-elf-objcopy -O verilog firmware.elf /dev/stdout > firmware.hex

attosoc_tb.vvp: attosoc_tb.v attosoc.v picorv32.v
	iverilog -s testbench -o $@ $^

attosoc_sim: attosoc_tb.vvp firmware.hex
	vvp -N $<

attosoc.json: io_wrapper.v attosoc.v picorv32.v firmware.hex
	yosys -p "synth_ecp5 -top top -json $@" io_wrapper.v attosoc.v picorv32.v

attosoc_out.config: attosoc.json
	nextpnr-ecp5 --45k --package CABGA381 --json $< --textcfg $@ --no-tmdriv

attosoc.bit: attosoc_out.config
	ecppack $< $@

clean:
	rm *.vvp *.vcd *.elf *.bin *.hex *.bit *.svf *_out.config *.json

.PHONY: attosoc_sim clean prog
.PRECIOUS: attosoc.json attosoc_out.config attosoc.bit
