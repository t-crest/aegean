#ifndef _request_ctrl_
#define _request_ctrl_

#include "globals.h"

#ifdef REALTIME
#include <comedilib.h> /* AD/DA driver */
#include "rtai_shm.h" /* periodic RT */
#include "rtai_sem.h" /* semaphores */
#endif

#include <stdio.h> /* printf */
#include <stdbool.h> /* boolean */
#include <stdlib.h> /* atoi atof */
#include <sys/mman.h>
#include <sched.h>
#include <pthread.h>
#include <math.h>
#include "util.h"
#include "globals.h"
#include "queue.h"

void *request_ctrl_run(void *no);

#endif /* _request_ctrl_ */
