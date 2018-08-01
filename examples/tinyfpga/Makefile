PROJ=morse

all: ${PROJ}.bit

%.json: %.v
	yosys -p "synth_ecp5 -noccu2 -nomux -nodram -json $@" $<

%.bit: %.json
	nextpnr-ecp5 --json $< --basecfg empty_85k.config --bit $@  --textcfg blinky_out.config --85k --package CSFBGA285

prog: ${PROJ}.bit
	tinyprog -p $<
