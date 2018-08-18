start:
    li s0, 2
    li s1, 0x02000000
outerloop:
    addi s0, s0, 1
    andi s0, s0, 0xff
    li s2, 2
innerloop:
    bge s2, s0, prime
    add a0, s0, 0
    add a1, s2, 0
    jal ra, divtest
    beq a0, x0, notprime
    addi s2, s2, 1
    j innerloop
prime:
    sw s0, 0(s1)
notprime:
    j outerloop

divtest: 
    li t0, 1
divloop:
    sub a0, a0, a1
    bge a0, t0, divloop
    jr ra
