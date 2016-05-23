/*
	Copyright (c) 	2015 Gary Sims
					2014 CurlyMo <curlymoo1@gmail.com>
					2012 Gordon Henderson

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdlib.h>
#include <ctype.h>
#include <poll.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/ioctl.h>

#include <linux/types.h>

#include "ci20.h"

#define NUM_PINS	22

#define	GPIO_BASE	0x10010000
#define PAGE_SIZE	0x1000
#define PAGE_MASK 	(PAGE_SIZE - 1)

#define PIN 	0x00 // PORT PIN Level Register
#define INTC	0x18 // PORT Interrupt Clear Register
#define MSKS	0x24 // PORT Interrupt Mask Set Register
#define PAT1S	0x34 // PORT Pattern 1 Set Register
#define PAT1C	0x38 // PORT Pattern 1 Clear Register
#define PAT0	0x40 // PORT Pattern 0 Register
#define PAT0S 	0x44 // PORT Pattern 0 Set Register
#define PAT0C 	0x48 // PORT Pattern 0 Clear  Register

static int pinModes[NUM_PINS];

static int pinToGpio[NUM_PINS] = {
		124, // wiringX # 0 - Physical pin  7 - GPIO 1
		122, // wiringX # 1 - Physical pin  11 - GPIO 2
		123, // wiringX # 2 - Physical pin  13 - GPIO 3
		125, // wiringX # 3 - Physical pin  15 - GPIO 4
		161, // wiringX # 4 - Physical pin  16 - GPIO 5
		162, // wiringX # 5 - Physical pin  18 - GPIO 6
		136, // wiringX # 6 - Physical pin  22 - GPIO 7
		126, // wiringX # 7 - Physical pin  3 - IC21_SDA
		127, // wiringX # 8 - Physical pin  5 - I2C1_SCK
		144, // wiringX # 9 - Physical pin  24 - SSI1_CE0
		146, // wiringX # 10 - Physical pin  26 - SSI1_CE1
		145, // wiringX # 11 - Physical pin  19 - SSI0_DT
		142, // wiringX # 12 - Physical pin  21 - SSI0_DR
		143, // wiringX # 13 - Physical pin  23 - SSI0_CLK
		163, // wiringX # 14 - Physical pin  8 - UART0_TXD
		160, // wiringX # 15 - Physical pin  10 - UART0_RXD
		52,  // wiringX # 16 - Expander 2 pin 6 - MOSI1
		53,  // wiringX # 17 - Expander 2 pin 7 - CE1
		60,  // wiringX # 18 - Expander 2 pin 4 - SCK1
		61,  // wiringX # 19 - Expander 2 pin 5 - MISO1
		62,  // wiringX # 20 - Expander 2 pin 8 - GPC
		63,  // wiringX # 21 - Expander 2 pin 3 - CE0
};

static int sysFds[64] = {
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
};

static volatile unsigned char *gpio;

static unsigned int gpioReadl(unsigned int gpio_offset) {
	return *(unsigned int *)(gpio + gpio_offset);
}

static void gpioWritel(unsigned int gpio_offset, unsigned int gpio_val) {
	*(unsigned int *)(gpio + gpio_offset) = gpio_val;
}

int ci20ValidGPIO(int pin) 
{
	if(pinToGpio[pin] != -1) {
		return 0;
	}
	return -1;
}


int setup(void) 
{
	int fd;

	if((fd = open("/dev/mem", O_RDWR | O_SYNC )) < 0) {
		fprintf(stderr, "ci20->setup: Unable to open /dev/mem");
		return -1;
	}
	off_t addr = GPIO_BASE & ~PAGE_MASK;
	gpio = (unsigned char *)mmap(0, PAGE_SIZE, PROT_READ|PROT_WRITE, MAP_SHARED, fd, addr);

	if((int32_t)gpio == -1) {
		fprintf(stderr, "ci20->setup: mmap (GPIO) failed");
		return -1;
	}

	return 0;
}

int ci20DigitalRead(int pin)
{
	// p is the port number (0,1,2,3,4,5)
	// o is the pin offset (0-31) inside the port
	// n is the absolute number of a pin (0-127), regardless of the port
	unsigned int p, o, n;
	unsigned int r;

	n = pinToGpio[pin];
	p = (n) / 32;
	o = (n) % 32;

	r = gpioReadl((PIN + (p)*0x100));

	if(((r) & (1 << (o))) == 0) {	
		return LOW;
	} else {
		return HIGH;
	}
}

int ci20DigitalWrite(int pin, int value) 
{
	// p is the port number (0,1,2,3,4,5)
	// o is the pin offset (0-31) inside the port
	// n is the absolute number of a pin (0-127), regardless of the port
	unsigned int p, o, n;

	n = pinToGpio[pin];
	p = (n) / 32;
	o = (n) % 32;
	
	if(value==0) {
		gpioWritel((PAT0C + (p)*0x100), (1 << (o)));	
	} else {
		gpioWritel((PAT0S + (p)*0x100), (1 << (o)));
	}
		
	return 0;
}

int ci20PinMode(int pin, int mode) 
{
	// p is the port number (0,1,2,3,4,5)
	// o is the pin offset (0-31) inside the port
	// n is the absolute number of a pin (0-127), regardless of the port
	unsigned int p, o, n;

	n = pinToGpio[pin];
	p = (n) / 32;
	o = (n) % 32;

	if(mode==INPUT) {
		gpioWritel((INTC + (p)*0x100), (1 << (o)));
		gpioWritel((MSKS + (p)*0x100), (1 << (o)));
		gpioWritel((PAT1S + (p)*0x100), (1 << (o)));
		gpioWritel((PAT0C + (p)*0x100), (1 << (o)));
	} else {
		gpioWritel((INTC + (p)*0x100), (1 << (o)));
		gpioWritel((MSKS + (p)*0x100), (1 << (o)));
		gpioWritel((PAT1C + (p)*0x100), (1 << (o)));
		gpioWritel((PAT0C + (p)*0x100), (1 << (o)));
	}
	pinModes[pin] = mode;
	
	return 0;
}


int ci20GC(void)
{
	int i = 0, fd = 0;
	char path[35];
	FILE *f = NULL;

	for(i=0;i<NUM_PINS;i++) {
		if(pinModes[i] == OUTPUT) {
			ci20PinMode(i, INPUT);
		} else if(pinModes[i] == SYS) {
			sprintf(path, "/sys/class/gpio/gpio%d/value", pinToGpio[i]);
			if((fd = open(path, O_RDWR)) > 0) {
				if((f = fopen("/sys/class/gpio/unexport", "w")) == NULL) {
					fprintf(stderr, "ci20->gc: Unable to open GPIO unexport interface: %s", strerror(errno));
				}

				fprintf(f, "%d\n", pinToGpio[i]);
				fclose(f);
				close(fd);
			}
		}
		if(sysFds[i] > 0) {
			close(sysFds[i]);
			sysFds[i] = -1;
		}
	}

	if(gpio) {
		munmap((void *)gpio, PAGE_SIZE);
	}
	return 0;
}


