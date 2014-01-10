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

#include "request_ctrl.h"

/*#define PERIOD 1000000*/
#define PERIOD 200000
#define SAMPLE_DELAY 25000
#define _PI_ 3.14159265359
#define BELT_DIST 530000

/* #define a -0.00370580
#define b 0.02953184
#define c -0.06842787
#define d 1.07479287 */
#define a -0.0042083
#define b 0.035900
#define c -0.0921056
#define d 1.0982733
void *request_ctrl_run(void *no){
	RTIME period = PERIOD;
	struct sched_param p;
	RT_TASK *task_ptr;
	lsampl_t presence,beltspeed;
	int adinput, result;
	int start_dist = 0;
	int end_dist = 0;
	int length = 0;
	bool blocked = false;
	bool enqueue = false;
	enum stick_size size = SMALL;

	rt_init(nam2num("h6req"), 5, task_ptr);

	p.sched_priority = sched_get_priority_max(SCHED_FIFO);
	sched_setscheduler(0, SCHED_FIFO, &p);


	rt_task_make_periodic_relative_ns(task_ptr, period, period);

	/* puts("Requester started"); */
	while (done == 0) {
		result = comedi_data_read_delayed(com,0,2,0,AREF_GROUND,&presence,SAMPLE_DELAY);
		if( result < 1){
			printf("Failed to read data: %d\n", result);
			continue;
		}

		result = comedi_data_read_delayed(com,0,1,0,AREF_GROUND,&beltspeed,SAMPLE_DELAY);
		if( result < 1){
			printf("Failed to read data: %d\n", result);
			continue;
		}
		double tach = (((int)beltspeed)-32768)/3276.7;
		tach = (a*pow(tach, 3.0) + b*pow(tach, 2.0) + c*tach + d)*tach;
		/*double umps = tach*76.0*1000.0*1000.0*_PI_/(2.6*6*60.0);*/
		double umps = tach*255086.58298378663047346249693295; //76.0*1000.0*1000.0*_PI_/(2.6*6*60.0) = 255086.5829
		int delta_dist = ((int)(umps*PERIOD/1000000000.0));
		distance = distance + delta_dist;

		adinput = ((int)presence)-32768;
		if (adinput > 7200) { //nothing blocking
			if (blocked) { //last sample something was there, so record end distance and calculate length
				enqueue = true;
				end_dist = distance;
				length = end_dist - start_dist;
				/* printf("length: %.2f mm\n", length/1000.0);  */
				if (length < 70000){
					if (length < 40000)
						printf("Warning! Very short stick detected\n");
					/*pos = -1;*/
					size = SMALL;
				}
				else if (length < 94000){
					/*pos = 0;*/
					size = MEDIUM;
				}
				else{
					if (length > 120000)
						printf("Warning! Very long stick detected\n");
					/*pos = 1;*/
					size = LARGE;
				}
			}
			blocked = false;
		} else { //something is blocking
			if (!(blocked)) { //last sample nothing was there, so record start distance
				start_dist = distance;
			}
			blocked = true;
		}

		if(enqueue){
			struct request r = { .dist = distance + BELT_DIST - 400000.0 * (40000.0/umps), .size = size};
			//struct request r = { .dist = distance + BELT_DIST , .size = size};
			send_req(&r);
			enqueue = false;
		}
		//printf("tach %.4fV - umps: %.4fum/s - delta_dist: %d um - total distance %d um\n",tach, umps, delta_dist, distance);
		rt_task_wait_period();
	}
	/*rt_task_wait_period();*/
	comedi_data_write(com,0,2,0,AREF_GROUND,32767);
	rt_task_wait_period();
	rt_delete(task_ptr);
	/* puts("Requester closed"); */
	return NULL;
}
