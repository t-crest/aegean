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

#include "statistics.h"

#define PERIOD 32000000

void *statistics_run(void *no){
	int small = 0;
	int medium = 0;
	int large = 0;
	RTIME period = PERIOD;
	struct sched_param p;
	RT_TASK *task_ptr;

	rt_init(nam2num("h6sta"), 8, task_ptr);

	p.sched_priority = sched_get_priority_max(SCHED_FIFO);
	sched_setscheduler(0, SCHED_FIFO, &p);

	rt_task_make_periodic_relative_ns(task_ptr, period, period);

	FILE *f = fopen("stats.txt", "w");
	if (f == NULL)
	{
	    printf("Error opening file!\n");
	    exit(1);
	}
	/* puts("Stats started"); */

	while(done == 0){
		enum stick_size s;
		if(stats == -1) {
			stats = 0;
			small = 0;
			medium = 0;
			large = 0;
			fclose(f);
			FILE *f = fopen("stats.txt", "w"); /* purge old file */
		}
		if(stats == 1) {
			stats = 0;
			printf("Sorted so far:\tSmall: %d\tMedium: %d\tLarge: %d\n",small,medium,large);
		}
		if(!retrieve_stat(&s)){
			rt_task_wait_period();
			continue;
		}
		char stat[10];
		switch(s){
			case SMALL:
				strncpy(stat,"Small",5);
				stat[5] = '\0';
				small++;
				break;
			case MEDIUM:
				strncpy(stat,"Medium",6);
				stat[6] = '\0';
				medium++;
				break;
			case LARGE:
				strncpy(stat,"Large",5);
				stat[5] = '\0';
				large++;
				break;
		}
		fprintf(f, "%s\n", stat);
	}
	fprintf(f,"In total sorted: \n\tSmall:\t%d\n\tMedium:\t%d\n\tLarge:\t%d\n",small,medium,large);
	fclose(f);
	rt_task_wait_period();
	rt_delete(task_ptr);
	/* puts("Stats closed"); */
	return NULL;
}
