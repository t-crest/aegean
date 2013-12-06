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

