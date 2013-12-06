#ifndef _statistics_
#define _statistics_

#include "globals.h"

#ifdef REALTIME
#include "rtai_shm.h" /* periodic RT */
#include "rtai_sem.h" /* semaphores */
#endif

#include <stdio.h> /* printf */
#include <stdlib.h> /* atoi atof */
#include <sys/mman.h>
#include <sched.h>
#include <pthread.h>

#include "queue.h"
#include "util.h"

void *statistics_run(void *no);

#endif /* _statistics_ */