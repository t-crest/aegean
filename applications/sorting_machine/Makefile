UNAME := $(shell uname)
ifneq ($(UNAME),Linux)
	CC = gcc -pthread 
	CFLAGS = -Wall -O1 
	LDFLAGS = 
	LIBS = 
else
	CC = gcc -pthread 
	CFLAGS = -Wall -O1    -I /usr/realtime/include -I /usr/local/include/sdlio 
	LDFLAGS = -L /usr/realtime/lib -L /usr/local/include/sdlio -lcomedi -lm 
	LIBS =  -lreadline -ltermcap -lcomedi
endif



OBJS = queue.o regul_fixed.o regul.o util.o statistics.o belt_motor_ctrl.o skid_motor_ctrl.o request_ctrl.o serve_ctrl.o operator.o

PROGS = operator

all:	$(PROGS)

operator: $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^ $(LIBS)



clean:
	-rm *.o
	-rm $(PROGS)

doc:	$(PROGS:=.ps)

%.ps:	%.c
	a2ps -Ma4 -1 -o $@ $<
#	a2ps -Ma4 -1 --sides=duplex -o $@ $<
