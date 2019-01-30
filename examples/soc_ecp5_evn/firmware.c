#include <stdint.h>
#include <stdlib.h>
#include <math.h>

#include "printf.h"

#define LED (*(volatile uint32_t*)0x02000000)

#define reg_uart_clkdiv (*(volatile uint32_t*)0x02000004)
#define reg_uart_data (*(volatile uint32_t*)0x02000008)

void _putchar(char c)
{
    if (c == '\n')
        _putchar('\r');
    reg_uart_data = c;
}

#define uartchar _putchar

void print(const char *p)
{
    while (*p)
        uartchar(*(p++));
}

void trap()
{
    print("TRAP\r\n");
}

void delay() {
    for (volatile int i = 0; i < 250000; i++)
        ;
}

int main() {
    reg_uart_clkdiv = 416;
    int count = 0;
    while (1) {
        LED = ++count;
#if 0
	asm("ebreak");
	*((int*)0x0000700f) = 1;
#endif
        //print("hello world\n");
        //printf("hello world %d\n", count);
        printf("hello printf: %d %f\n", count, sqrt(count));

        delay();
    }
}
