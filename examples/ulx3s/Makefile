all: blinky.bit

blinky.json: blinky.v
	yosys -p "synth_ecp5 -json blinky.json" blinky.v

blinky_out.config: blinky.json
	nextpnr-ecp5 --json blinky.json --textcfg blinky_out.config --45k

blinky.bit: blinky_out.config
	ecppack blinky_out.config blinky.bit
