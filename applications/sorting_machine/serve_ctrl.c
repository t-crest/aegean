#include "serve_ctrl.h"

#define PERIOD 7307600

char sticktopos(char room){
	switch(room){
		case 1:
			return -1;
		case 2:
			return 0;
		case 3:
			return 1;
		default:
			return 0;
	}
}

void *serve_ctrl_run(void *no){
	RTIME period = PERIOD;
	struct sched_param p;
	RT_TASK *task_ptr;

	rt_init(nam2num("h6ser"), 5, task_ptr);

	p.sched_priority = sched_get_priority_max(SCHED_FIFO);
	sched_setscheduler(0, SCHED_FIFO, &p);
	
	rt_task_make_periodic_relative_ns(task_ptr, period, period);

/*	puts("Server started"); */

	while (done == 0) {
		struct request r;
		if(!retrieve_req(&r)){
			rt_task_wait_period();
			continue;
		}
		
		switch(r.size){
			case SMALL:
				pos = sticktopos(small_room);
				break;
			case MEDIUM:
				pos = sticktopos(medium_room);
				break;
			case LARGE:
				pos = sticktopos(large_room);
				break;
			default:
				break;
		}
/*		printf("Recieved size: %d\n, New pos: %d",(int)r.size,pos); */
		send_stat(&(r.size));
		rt_task_wait_period();
		while(r.dist > distance){
			rt_task_wait_period();
		}
		
	}
	rt_task_wait_period();
	rt_delete(task_ptr);
/*	puts("Server closed"); */
	return NULL;
}
