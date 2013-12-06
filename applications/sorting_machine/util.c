#include "util.h"

void rt_init(int pid, int priority, RT_TASK *task_ptr){
#ifdef REALTIME
	rt_allow_nonroot_hrt();
	mlockall(MCL_FUTURE);
	task_ptr = rt_task_init(pid,priority,0,0); /* required for semaphores to work */
	if (task_ptr == NULL) {
		printf("Task pointer is zero!!\n");
		return;
	}
#endif
	return;
}

void rt_delete(RT_TASK *task_ptr){
#ifdef REALTIME
	rt_task_delete(task_ptr);
#endif
	return;
}
