PROJ=morse

all: ${PROJ}.bit

%.json: %.v
	yosys -p "synth_ecp5 -noccu2 -nomux -nodram -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --basecfg empty_85k.config --textcfg $@ --85k --package CSFBGA285

%.bit: %_out.config
	ecppack $< $@

prog: ${PROJ}.bit
	tinyprog -p $<
