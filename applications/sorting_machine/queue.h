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