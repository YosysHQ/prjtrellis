PROJ=demo
CONSTR=versa.lpf
TRELLIS?=/usr/share/trellis

all: ${PROJ}.bit

pattern.vh: make_14seg.py text.in
	python3 make_14seg.py < text.in > pattern.vh

%.json: %.v pattern.vh
	yosys -p "synth_ecp5 -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --lpf ${CONSTR} --textcfg $@ --um5g-45k --package CABGA381

%.bit: %_out.config
	ecppack --svf-rowsize 100000 --svf ${PROJ}.svf $< $@

${PROJ}.svf: ${PROJ}.bit

prog: ${PROJ}.svf
	openocd -f ${TRELLIS}/misc/openocd/ecp5-versa5g.cfg -c "transport select jtag; init; svf $<; exit"

.PHONY: prog
.PRECIOUS: ${PROJ}.json ${PROJ}_out.config
