PROJ=blinky
TRELLIS?=/usr/share/trellis

all: ${PROJ}.bit

%.json: %.v
	yosys -p "synth_ecp5 -top top -json $@" $<

%_out.config: %.json
	nextpnr-ecp5 --json $< --textcfg $@ --um5g-85k --package CABGA381 --lpf ecp5evn.lpf

%.bit: %_out.config
	ecppack --svf ${PROJ}.svf $< $@

${PROJ}.svf : ${PROJ}.bit

prog: ${PROJ}.svf
	openocd -f ${TRELLIS}/misc/openocd/ecp5-evn.cfg -c "transport select jtag; init; svf $<; exit"

clean:
	rm -f *.svf *.bit *.config *.json

.PHONY: all prog clean
