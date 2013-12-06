#ifndef _skid_motor_ctrl_
#define _skid_motor_ctrl_

#include "globals.h"

#ifdef REALTIME
#include <comedilib.h> /* AD/DA driver */
#include "rtai_shm.h" /* periodic RT */
#include "rtai_sem.h" /* semaphores */
#endif
#include <stdio.h> /* printf */
#include <stdlib.h> /* atoi atof */
#include <sys/mman.h>
#include <sched.h>
#include <pthread.h>
#include "util.h"
#include "regul_fixed.h"

#define fixedPoint 1024
#define left 6000
#define middle 0
#define right -6000

/*extern comedi_t* com;
extern short int done; 
extern char pos;*/

void *skid_motor_ctrl_run(void *no);

#endif /* _skid_motor_ctrl_ */
