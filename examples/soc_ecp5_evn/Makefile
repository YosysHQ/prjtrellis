firmware.elf: sections.lds start.S firmware.c printf.c
	riscv32-unknown-elf-gcc -march=rv32imc -Os -mabi=ilp32 -Wl,-Bstatic,-T,sections.lds,--strip-debug -ffreestanding -nostdlib -o firmware.elf start.S firmware.c -DPRINTF_DISABLE_SUPPORT_LONG_LONG -DPRINTF_DISABLE_SUPPORT_PTRDIFF_T printf.c -lm -lc -lgcc
	#/opt/riscv32imc/bin/riscv32-unknown-elf-gcc -march=rv32imc -Os -mabi=ilp32 -Wl,-Bstatic,-T,sections.lds,--strip-debug -ffreestanding -nostdlib -o firmware.elf start.S firmware.c -DPRINTF_DISABLE_SUPPORT_LONG_LONG -DPRINTF_DISABLE_SUPPORT_PTRDIFF_T printf.c -lm -lc -lgcc

firmware.bin: firmware.elf
	riscv32-unknown-elf-objcopy -O binary firmware.elf /dev/stdout > firmware.bin

firmware.hex: firmware.bin
	python3 makehex.py $^ 16384 > $@

attosoc_tb.vvp: attosoc_tb.v attosoc.v picorv32.v simpleuart.v firmware.hex
	iverilog -s testbench -o $@ attosoc_tb.v attosoc.v picorv32.v simpleuart.v

attosoc_sim: attosoc_tb.vvp firmware.hex
	vvp -N $<

attosoc.json: top.v attosoc.v picorv32.v pll.v firmware.hex
	yosys -p "synth_ecp5 -json $@ -top top" top.v pll.v attosoc.v picorv32.v simpleuart.v

attosoc_out.config: attosoc.json ecp5evn.lpf
	nextpnr-ecp5 --json attosoc.json --lpf ecp5evn.lpf --basecfg ../../misc/basecfgs/empty_lfe5um5g-85f.config --textcfg $@ --um5g-85k --freq 50

attosoc.bit: attosoc_out.config
	ecppack $< $@

%.svf: %.bit
	../../tools/bit_to_svf.py $< $@

prog: attosoc.svf
	openocd -f ../../misc/openocd/ecp5-evn.cfg -c "transport select jtag; init; svf $<; exit"

.PHONY: attosoc_sim clean prog
.PRECIOUS: attosoc.json attosoc_out.config attosoc.bit
