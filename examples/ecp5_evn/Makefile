PROJ=blinky

all: ${PROJ}.bit


%.json: %.v
	yosys -p "synth_ecp5 -noccu2 -nobram -nomux -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --basecfg ../../misc/basecfgs/empty_lfe5um5g-85f.config --textcfg $@ --um5g-85k --package CABGA381

%.bit: %_out.config
	ecppack $< $@

%.svf: %.bit
	../../tools/bit_to_svf.py $< $@

prog: ${PROJ}.svf
	openocd -f ../../misc/openocd/ecp5-evn.cfg -c "transport select jtag; init; svf $<; exit"

.PHONY: prog
