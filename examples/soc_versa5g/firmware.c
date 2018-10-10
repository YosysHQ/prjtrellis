#include <stdint.h>

#define LED (*(volatile uint32_t*)0x02000000)

void delay() {
   for (volatile int i = 0; i < 50000; i++)
	   ;
}

int main() {
   while (1) {
	LED = 0xFF;
	delay();
	LED = 0x00;
	delay();
   }
}
