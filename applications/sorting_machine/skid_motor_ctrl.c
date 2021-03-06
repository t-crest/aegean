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

#include "skid_motor_ctrl.h"

void *skid_motor_ctrl_run(void *no){
	RTIME period = 7307600;
	/* int b0 = ((int) 47.95*fixedPoint);
	int b1 = ((int)-38.54*fixedPoint);
	int a1 = ((int) -0.2953*fixedPoint); */
	int b0 = ((int) 32.81*fixedPoint);
	int b1 = ((int)-26.37*fixedPoint);
	int a1 = ((int) -0.2953*fixedPoint);
	struct sched_param p;
	RT_TASK *task_ptr;
	lsampl_t in_data;
	int e, adinput, target;
	int result, output;

	rt_init(nam2num("h6skid"), 6, task_ptr);

	p.sched_priority = sched_get_priority_max(SCHED_FIFO);
	sched_setscheduler(0, SCHED_FIFO, &p);

	regul_init_fixed();

	rt_task_make_periodic_relative_ns(task_ptr, period, period);

	/* puts("Skidmotor started"); */
	while (done == 0) {
		result = comedi_data_read_delayed(com,0,0,0,AREF_GROUND,&in_data,50000);
		if( result < 1){
			printf("Failed to read data: %d\n", result);
			rt_task_wait_period();
			continue;
		}
		adinput = ((int)in_data)-32768;
		if (pos > 0) { target = left; }
		else if (pos < 0) { target = right; }
		else { target = middle; }
		e = target - adinput;

		/* output = ((int)regul_out_fixed(e, &b0)/(fixedPoint)+32768); */
		output = ((int)regul_out_fixed(e, &b0)+32768);
		if (output < 0) { output = 0; }
		else if (output > 65535) { output = 65535; }
		comedi_data_write(com,1,0,0,AREF_GROUND,output);

		regul_update_fixed(e, &b1, &a1);
		rt_task_wait_period();
	}
	comedi_data_write(com,1,0,0,AREF_GROUND,32767);
	rt_task_wait_period();
	rt_delete(task_ptr);
	/* puts("Skidmotor closed"); */
	return NULL;
}

