#include "regul_fixed.h"

static struct {
	signed long long dummy;
	signed long long u;
}states;

void regul_init_fixed(void){
	states.dummy = 0;
	states.u = 0;
}

long long regul_out_fixed(signed int e,signed int* b0){
	signed long long u;
	u = (e * (*b0)) >> 10;
	states.u = u + states.dummy;
	return states.u;
}

void regul_update_fixed(signed int e,signed int* b1,signed int* a1){
	signed long long u1, d1;
	u1 = (states.u * (*a1)) >> 10;
	d1 = (e * (*b1)) >> 10;
	states.dummy = d1 - u1;
}

