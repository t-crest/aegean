#ifndef _regul_
#define _regul_

void regul_init(void);

double regul_out(double e,double* b0);

void regul_update(double e,double* b1,double* a1);

#endif /* _regul_ */