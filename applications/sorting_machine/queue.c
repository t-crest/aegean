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

#include "queue.h"


/**
 * The initialize_message_passing() initializes the  owner and port_id of the
 * queue.
 */
void init_queue(void) {
    /*rt_sem_wait(&queue_lock);*/
    request_queue.head = 0;
    request_queue.tail = 0;
    stat_queue.head = 0;
    stat_queue.tail = 0;
    /*rt_sem_signal(&queue_lock);*/
    return;
}


int send_req(struct request* r) {
    /*rt_sem_wait(&queue_lock);*/

    const int head = request_queue.head;
    const int tail = request_queue.tail;

    bool report = true;
    int new_tail = 0;
    // Check if there is room in the queue
    if (tail == MAX_NUMBER_OF_WAITING_REQUESTS - 1) {
        if (head == 0) {
            // The queue is full, return false.
            report = false;
        } else {
            new_tail = 0;
        }
    } else {
        if (tail + 1 == head) {
            // The queue is full, return false.
            report = false;
        } else {
            new_tail = tail + 1;
        }
    }
    if(report == true){
        request_queue.requests[tail] = *r;
        request_queue.tail = new_tail;
    }
    /*rt_sem_signal(&queue_lock);*/
    return report;
}



int retrieve_req(struct request* r){

    /*rt_sem_wait(&queue_lock);*/

    const int head = request_queue.head;
    const int tail = request_queue.tail;
    bool report;
    int new_head;

    if (head == tail) { // If the queue is empty, no messages to return.
        report = false;
    } else {
        if (head == MAX_NUMBER_OF_WAITING_REQUESTS - 1) {
            new_head = 0;
        } else {
            new_head = head + 1;
        }
        struct request req = request_queue.requests[head];
        *r = req;
        request_queue.head = new_head;
        report = true;
    }
    /*rt_sem_signal(&queue_lock);*/
    return report;
}


int send_stat(enum stick_size* s) {
    /*rt_sem_wait(&queue_lock);*/

    const int head = stat_queue.head;
    const int tail = stat_queue.tail;

    bool report = true;
    int new_tail = 0;
    // Check if there is room in the queue
    if (tail == MAX_NUMBER_OF_WAITING_STATS - 1) {
        if (head == 0) {
            // The queue is full, return false.
            report = false;
        } else {
            new_tail = 0;
        }
    } else {
        if (tail + 1 == head) {
            // The queue is full, return false.
            report = false;
        } else {
            new_tail = tail + 1;
        }
    }
    if(report == true){
        stat_queue.stat[tail] = *s;
        stat_queue.tail = new_tail;
    }
    /*rt_sem_signal(&queue_lock);*/
    return report;
}



int retrieve_stat(enum stick_size* s){

    /*rt_sem_wait(&queue_lock);*/

    const int head = stat_queue.head;
    const int tail = stat_queue.tail;
    bool report;
    int new_head;

    if (head == tail) { // If the queue is empty, no messages to return.
        report = false;
    } else {
        if (head == MAX_NUMBER_OF_WAITING_STATS - 1) {
            new_head = 0;
        } else {
            new_head = head + 1;
        }
        enum stick_size stat = stat_queue.stat[head];
        *s = stat;
        stat_queue.head = new_head;
        report = true;
    }
    /*rt_sem_signal(&queue_lock);*/
    return report;
}
