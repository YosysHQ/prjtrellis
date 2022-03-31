PROJ=morse

all: ${PROJ}.bit

%.json: %.v
	yosys -p "synth_ecp5 -top top -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --textcfg $@ --85k --package CSFBGA285

%.bit: %_out.config
	ecppack $< $@

clean:
	rm *.bit *.svf *_out.config *.json

prog: ${PROJ}.bit
	tinyprog -p $<

.PHONY: clean

