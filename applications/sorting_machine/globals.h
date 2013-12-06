#ifndef _globals_
#define _globals_

#define REALTIME

#ifdef REALTIME
#include <comedilib.h> /* AD/DA driver */
#include "rtai_sem.h" /* semaphores */
#else
#define comedi_t int
#define SEM int
#define RT_TASK int
#define RTIME int
#define lsampl_t int
#define nam2num(x) 1
#define rt_task_make_periodic_relative_ns(x,y,z)
#define rt_task_wait_period()
/*#define rt_task_delete(a)*/
#define rt_typed_sem_init(a,b,c)
#define rt_sem_wait(a)
#define rt_sem_signal(a)
#define comedi_open(a) 1
#define comedi_data_read_delayed(a,b,c,d,x,y,z) 100
#define comedi_data_write(a,b,c,d,e,f)
#define comedi_close(a)
#endif

extern short int done;
extern short int stats;
extern comedi_t* com;
extern char pos;
extern short int speed;
extern unsigned int distance;  /* distance of belt travel in um */

extern char small_room;
extern char medium_room;
extern char large_room;

/* Locks */
/*extern SEM queue_lock;*/

#endif /* _globals_ */
