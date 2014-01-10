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

#include "belt_motor_ctrl.h"

#define PERIOD 7307600
#define _PI_ 3.141592654

void *belt_motor_ctrl_run(void *no){
	double b0 = 0.9747;
	double b1 = -0.8805;
	double a1 = -1;
	struct sched_param p;
	RT_TASK *task_ptr;
	RTIME period = 7307600;
	int result, output;
	lsampl_t in_data;
	double adinput, e;


	rt_init(nam2num("mbch6"), 6, task_ptr);

	p.sched_priority = sched_get_priority_max(SCHED_FIFO);
	sched_setscheduler(0, SCHED_FIFO, &p);


	regul_init();

	rt_task_make_periodic_relative_ns(task_ptr, period, period);
	/* puts("Beltmotor started"); */

	while (done == 0) {
		result = comedi_data_read_delayed(com,0,1,0,AREF_GROUND,&in_data,50000);
		if( result < 1){
			printf("Failed to read data: %d\n", result);
			continue;
		}
		double tach = (((int)in_data)-32768)/3276.7;
		e = ((double)speed)/25.5 - tach;
		output = (int)(regul_out(e, &b0)*3276.7)+32767;
		comedi_data_write(com,1,1,0,AREF_GROUND,output);
		regul_update(e, &b1, &a1);
		//printf("Tachometer value: %.1f\toutout value: %d\tspeed value: %d\n",tach,output,speed);
		/* Calculation of the new distance value */
		/*
		double umps = tach*76.0*1000.0*1000.0*_PI_/(2.6*6*60.0);
		int delta_dist = ((int)(umps*PERIOD/1000000000.0));
		distance = distance + delta_dist;
		*/

		rt_task_wait_period();

	}
	comedi_data_write(com,1,1,0,AREF_GROUND,32767);
	rt_task_wait_period();
	rt_delete(task_ptr);
	/* puts("Beltmotor closed"); */
	return NULL;
}
