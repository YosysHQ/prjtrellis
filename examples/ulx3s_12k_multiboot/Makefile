all: multiboot.mcs

%.json: %.v
	yosys -p "synth_ecp5 -top top -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --textcfg $@ --25k --package CABGA381 --lpf ulx3s.lpf

%.bit: %_out.config
	ecppack --idcode 0x21111043 $< $@


multiboot.bin: blinky1.bit blinky2.bit
	ecpmulti --input-idcode 0x41111043 --output-idcode 0x21111043 --flashsize 128 --input blinky1.bit --input blinky2.bit --address 0x00250000 $@

multiboot.mcs: multiboot.bin
	srec_cat $< -Binary -unfill 0xFF -Bit_Reverse=2 -Byte-Swap -o $@ -Intel

clean:
	rm -f *.svf *.bit *.config *.json multiboot.bin multiboot.mcs

.PHONY: all clean
.PRECIOUS: blinky1.json blinky1_out.config blinky1.bit blinky2.json blinky2_out.config blinky2.bit multiboot.bin multiboot.mcs
