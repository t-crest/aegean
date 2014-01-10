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
