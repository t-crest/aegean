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