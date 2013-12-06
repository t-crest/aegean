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
