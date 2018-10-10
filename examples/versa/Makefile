PROJ=demo

all: ${PROJ}.bit

pattern.vh: make_14seg.py text.in
	python3 make_14seg.py < text.in > pattern.vh

%.json: %.v pattern.vh
	yosys -p "synth_ecp5 -noccu2 -nomux -nodram -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --basecfg ../../misc/basecfgs/empty_lfe5um5g-45f.config --textcfg $@ --45k --package CABGA381

%.bit: %_out.config
	ecppack $< $@
