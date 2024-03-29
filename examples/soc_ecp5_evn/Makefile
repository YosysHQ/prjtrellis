TRELLIS?=/usr/share/trellis

firmware.elf: sections.lds start.s firmware.c
	riscv32-unknown-elf-gcc -march=rv32i -Wl,-Bstatic,-T,sections.lds,--strip-debug -ffreestanding -nostdlib -o firmware.elf start.s firmware.c

firmware.bin: firmware.elf
	riscv32-unknown-elf-objcopy -O binary firmware.elf /dev/stdout > firmware.bin

firmware.hex: firmware.bin
	python3 makehex.py $^ 4096 > $@

attosoc_tb.vvp: attosoc_tb.v attosoc.v picorv32.v simpleuart.v
	iverilog -s testbench -o $@ $^

attosoc_sim: attosoc_tb.vvp firmware.hex
	vvp -N $<

attosoc.json: top.v attosoc.v picorv32.v pll.v firmware.hex
	yosys -p "synth_ecp5 -top top -json $@ -top top" top.v pll.v attosoc.v picorv32.v simpleuart.v

attosoc_out.config: attosoc.json ecp5evn.lpf
	nextpnr-ecp5 --json attosoc.json --lpf ecp5evn.lpf --textcfg $@ --um5g-85k --freq 50 --package CABGA381

attosoc.bit: attosoc_out.config
	ecppack --svf-rowsize 100000 --svf attosoc.svf $< $@

%.svf: %.bit

prog: attosoc.svf
	openocd -f ${TRELLIS}/misc/openocd/ecp5-evn.cfg -c "transport select jtag; init; svf $<; exit"

clean:
	rm -f *.vvp *.vcd *.elf *.bin *.hex *.bit *.svf *_out.config *.json

.PHONY: attosoc_sim clean prog
.PRECIOUS: attosoc.json attosoc_out.config attosoc.bit
