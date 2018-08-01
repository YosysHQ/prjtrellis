all: blinky.bit

blinky.json: blinky.v
	yosys -p "synth_ecp5 -noccu2 -nomux -nodram -json blinky.json" blinky.v

blinky_out.config: blinky.json
	nextpnr-ecp5 --json blinky.json --basecfg ulx3s_empty.config --textcfg blinky_out.config --45k

blinky.bit: blinky_out.config
	ecppack blinky_out.config blinky.bit
