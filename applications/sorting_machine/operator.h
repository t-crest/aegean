#ifndef _operator_
#define _operator_

#include "globals.h"

#ifdef REALTIME
#include <comedilib.h> /* AD/DA driver */
#include "rtai_shm.h" /* periodic RT */
#include "rtai_sem.h" /* semaphores */
#endif
/*
#define DRYRUN
*/


#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "util.h"
#include "queue.h"

#include "serve_ctrl.h"
#include "request_ctrl.h"
#include "statistics.h"
#include "belt_motor_ctrl.h"
#include "skid_motor_ctrl.h"

RT_TASK *task_ptr;
pthread_t request_ctrl, serve_ctrl, statistics, belt_motor_ctrl, skid_motor_ctrl;



#endif /* _operator_ */
