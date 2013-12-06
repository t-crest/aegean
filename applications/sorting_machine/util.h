#ifndef _util_
#define _util_

#include "globals.h"

#ifdef REALTIME
#include "rtai_shm.h" /* periodic RT */
#endif
#include <stdio.h>

void rt_init(int pid, int priority, RT_TASK *task_ptr);

void rt_delete(RT_TASK *task_ptr);

#endif /* _util_ */
