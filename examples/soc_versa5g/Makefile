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

attosoc.json: top.v pll.v attosoc.v picorv32.v firmware.hex
	yosys -p "synth_ecp5 -json $@ -top top" top.v pll.v attosoc.v picorv32.v simpleuart.v

attosoc_out.config: attosoc.json versa.lpf
	nextpnr-ecp5 --json attosoc.json --lpf versa.lpf --basecfg ../../misc/basecfgs/empty_lfe5um5g-45f.config --textcfg $@ --um5g-45k --freq 50

attosoc.bit: attosoc_out.config
	ecppack $< $@

%.svf: %.bit
	../../tools/bit_to_svf.py $< $@

prog: attosoc.svf
	openocd -f ../../misc/openocd/ecp5-versa5g.cfg -c "transport select jtag; init; svf $<; exit"

.PHONY: attosoc_sim clean prog
.PRECIOUS: attosoc.json attosoc_out.config attosoc.bit
