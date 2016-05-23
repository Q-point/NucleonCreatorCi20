/*
	Copyright (c) 2014 CurlyMo <curlymoo1@gmail.com>

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

#ifndef _WIRING_X_CI20_H_
#define _WIRING_X_CI20_H_

#include <errno.h>
#include <syslog.h>

#ifndef	TRUE
#define	TRUE	(1==1)
#define	FALSE	(1==2)
#endif

#if !defined(PATH_MAX)
    #if defined(_POSIX_PATH_MAX)
        #define PATH_MAX _POSIX_PATH_MAX
    #else
        #define PATH_MAX 1024
    #endif
#endif

#define HIGH							1
#define LOW								0

#define INPUT							0
#define OUTPUT						1
#define	PWM_OUTPUT				2
#define	GPIO_CLOCK				3
#define	SOFT_PWM_OUTPUT		4
#define	SOFT_TONE_OUTPUT	5
#define	PWM_TONE_OUTPUT		6
#define SYS					7



int ci20ValidGPIO(int pin) ;
int setup(void) ;
int ci20DigitalRead(int pin);
int ci20DigitalWrite(int pin, int value);
int ci20PinMode(int pin, int mode);



#endif
