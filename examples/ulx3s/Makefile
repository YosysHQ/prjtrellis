all: blinky.bit hello.bit

hello.json: pll_120.v

IDCODE ?= 0x21111043 # 12f

%.json: %.v
	yosys -p "synth_ecp5 -json $@" $<

%.config: %.json
	nextpnr-ecp5 --json $< --textcfg $@ --25k

%.bit: %.config
	ecppack --idcode $(IDCODE) $< $@

%.svf: %.config
	ecppack --idcode $(IDCODE) --input $< --svf $@

%.flash: %.bit
	sudo ujprog $<
%.terminal: %.bit
	sudo ujprog -t -b 3000000 $<

pll_%.v:
	ecppll \
		-i 25 \
		-o $(subst pll_,,$(basename $@)) \
		-f $@
