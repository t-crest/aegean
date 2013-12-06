#ifndef _belt_motor_ctrl_
#define _belt_motor_ctrl_

#include "globals.h"

#ifdef REALTIME
#include <comedilib.h> /* AD/DA driver */
#include "rtai_shm.h" /* periodic RT */
#include "rtai_sem.h" /* semaphores */
#include <sys/mman.h>
#endif

#include <stdio.h> /* printf */
#include <stdlib.h> /* atoi atof */
#include <sched.h>
#include <pthread.h>
#include "regul.h"
#include "util.h"



void *belt_motor_ctrl_run(void *no);

#endif /* _belt_motor_ctrl_ */
