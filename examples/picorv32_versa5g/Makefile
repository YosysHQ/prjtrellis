firmware.elf: sections.lds firmware.s
	riscv32-unknown-elf-gcc -march=rv32i -Wl,-Bstatic,-T,sections.lds,--strip-debug -ffreestanding -nostdlib -o firmware.elf firmware.s

firmware.hex: firmware.elf
	riscv32-unknown-elf-objcopy -O verilog firmware.elf /dev/stdout > firmware.hex

attosoc_tb.vvp: attosoc_tb.v attosoc.v picorv32.v
	iverilog -s testbench -o $@ $^

attosoc_sim: attosoc_tb.vvp firmware.hex
	vvp -N $<

attosoc.json: io_wrapper.v attosoc.v picorv32.v firmware.hex
	yosys -p "synth_ecp5 -nomux -json $@ -top top" io_wrapper.v attosoc.v picorv32.v

attosoc_out.config: attosoc.json
	nextpnr-ecp5 --json $< --basecfg ../../misc/basecfgs/empty_lfe5um5g-45f.config --textcfg $@ --um5g-45k

attosoc.bit: attosoc_out.config
	ecppack $< $@

%.svf: %.bit
	../../tools/bit_to_svf.py $< $@

prog: attosoc.svf
	openocd -f ../../misc/openocd/ecp5-versa5g.cfg -c "transport select jtag; init; svf $<; exit"

.PHONY: attosoc_sim clean prog
.PRECIOUS: attosoc.json attosoc_out.config attosoc.bit
