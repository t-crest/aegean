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

#include "operator.h"

void thread_init(){
#ifndef  DRYRUN
	pthread_create(&statistics, NULL, statistics_run, NULL);
	pthread_create(&serve_ctrl, NULL, serve_ctrl_run, NULL);
	pthread_create(&skid_motor_ctrl, NULL, skid_motor_ctrl_run, NULL);
	pthread_create(&request_ctrl, NULL, request_ctrl_run, NULL);
	pthread_create(&belt_motor_ctrl, NULL, belt_motor_ctrl_run, NULL);
#endif
	return;
}

void thread_close(){
#ifndef DRYRUN
	pthread_join(statistics,NULL);
	pthread_join(serve_ctrl,NULL);
	pthread_join(skid_motor_ctrl,NULL);
	pthread_join(request_ctrl,NULL);
	pthread_join(belt_motor_ctrl,NULL);
#endif
	return;
}

short int done = 0;
short int stats = 0; /* -1: reset. 1: show */
comedi_t* com;
char pos = 0;
short int speed = 0;
unsigned int distance = 0;
char small_room = 1;
char medium_room = 2;
char large_room = 3;

int main(int argc, char const *argv[])
{
	char *input;
	size_t nbytes = 256;
	int bytes_read;
	input = (char *) malloc (nbytes+1);
	done = 0;
	speed = 0;
	small_room = 1;
	medium_room = 2;
	large_room = 3;
	rt_init(nam2num("maih6"),10,task_ptr);
	com = comedi_open("/dev/comedi2");

	/* Initialization of locks */
	/*rt_typed_sem_init(&queue_lock,1,BIN_SEM);*/

	/* Initialize the queue */
	init_queue();

	/* puts("Operator started"); */

	/* The order that the threads are started in might be important.
	 * We might need to insert wait()'s between the pthread_create()'s
	 */
	thread_init();

	strcpy(input, "help");
	while(done == 0){

		if (strncmp(input, "speed",5) == 0) {
			puts("Input the desired speed in m/s between 0.2 and 1.3:");
			fputs("... ",stdout);
			bytes_read = getline(&input, &nbytes, stdin);
			if (atof(input) > 1.3)
				speed = 130;
			else if (atof(input) < 0.05)
				speed = 0;
			else if (atof(input) < 0.2)
				speed = 20;
			else
				speed = floor(atof(input)*100);
			printf("Actual target speed: %.2f m/s\n", speed/100.0);
		}
		else if (strncmp(input, "sort",4) == 0) {
			puts("Input the the room (1 - 3) where the small sticks should go:");
			fputs("... ",stdout);
			bytes_read = getline(&input, &nbytes, stdin);
			if (atoi(input) > 3)
				small_room = 3;
			else if (atoi(input) < 1)
				small_room = 1;
			else
				small_room = atoi(input);
			puts("Input the the room (1 - 3) where the medium sticks should go:");
			fputs("... ",stdout);
			bytes_read = getline(&input, &nbytes, stdin);
			if (atoi(input) > 3)
				medium_room = 3;
			else if (atoi(input) < 1)
				medium_room = 1;
			else
				medium_room = atoi(input);
			puts("Input the the room (1 - 3) where the large sticks should go:");
			fputs("... ",stdout);
			bytes_read = getline(&input, &nbytes, stdin);
			if (atoi(input) > 3)
				large_room = 3;
			else if (atoi(input) < 1)
				large_room = 1;
			else
				large_room = atoi(input);
			printf("New room settings:");
			printf("\tSmall room: %d\n",small_room);
			printf("\tMedium room: %d\n",medium_room);
			printf("\tLarge room: %d\n",large_room);
		}
		else if (strncmp(input, "reset",5) == 0) {
			puts("Statistics reset");
			stats = -1;
		}
		else if (strncmp(input, "stats",5) == 0) {
			stats = 1;
		}
		else if (strncmp(input, "quit",4) == 0) {
			puts("Program terminated");
			speed = 0;
			done = 1;
			break;
		}
		else if (strncmp(input, "help",4) == 0) {
			puts("Help menu");
			puts("\tspeed : Set the speed of the belt");
			puts("\tsort  : Set the sorting sequence of the sticks");
			puts("\tstats : Show statistics");
			puts("\treset : Reset the statistics of the sorting sequence");
			puts("\thelp   : Shows this menu");
			puts("\tquit  : The program will terminate");
		}
		else
			puts("Command Unkown");

		fputs(">>> ",stdout);
		bytes_read = getline(&input, &nbytes, stdin);
		if (bytes_read == -1){
			puts("ERROR!");
			return 0;
		}

	}
	/* puts("Operator closing"); */

	thread_close();
	comedi_close(com);
	rt_delete(task_ptr);
	/* puts("Operator closed"); */
	return 0;
}
