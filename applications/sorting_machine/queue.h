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

#ifndef _QUEUE_
#define _QUEUE_

#include "globals.h"

#ifdef REALTIME
#include "rtai_sem.h" /* semaphores */
#endif

#include <stdbool.h> /* boolean */


#define MAX_NUMBER_OF_WAITING_REQUESTS 16
#define MAX_NUMBER_OF_WAITING_STATS 32

enum stick_size { SMALL=0, MEDIUM, LARGE };

struct request {
    unsigned int dist;
    enum stick_size size;
};

struct request_queue_t {
    struct request requests[MAX_NUMBER_OF_WAITING_REQUESTS];
    int head;
    int tail;
};

struct stat_queue_t {
    enum stick_size stat[MAX_NUMBER_OF_WAITING_STATS];
    int head;
    int tail;
};


struct request_queue_t request_queue;
struct stat_queue_t stat_queue;

//int request_enqueue(struct request r);
//struct request request_dequeue();

void init_queue(void);

int send_req(struct request* r);

int retrieve_req(struct request* r);


int send_stat(enum stick_size* s);

int retrieve_stat(enum stick_size* s);

#endif  /* QUEUE */
