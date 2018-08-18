start:
	li a0, 0x01
	li a1, 0x02000000
blink:
	sw a0, 0(a1)
	xor a0, a0, 0x01
	j blink
