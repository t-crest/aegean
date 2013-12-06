#include "regul.h"

static struct {
	double dummy;
	double u;
}states;

void regul_init(void){
	states.dummy = 0;
	states.u = 0;
}

double regul_out(double e,double* b0){
	states.u = states.dummy + e * (*b0);
	return states.u;
}

void regul_update(double e,double* b1,double* a1){
	states.dummy = e * (*b1) - states.u * (*a1);
}

