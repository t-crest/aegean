/*
 * Copyright Technical University of Denmark. All rights reserved.
 * This file is part of the T-CREST project.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *    1. Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *
 *    2. Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
 * NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * The views and conclusions contained in the software and documentation are
 * those of the authors and should not be interpreted as representing official
 * policies, either expressed or implied, of the copyright holder.
 *
 *##############################################################################
 * Authors:
 *    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
 *    Thomas Timm Andersen (ttan@elektro.dtu.dk)
 *##############################################################################
 */

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
