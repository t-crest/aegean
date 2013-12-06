#ifndef _regul_fixed_
#define _regul_fixed_

void regul_init_fixed(void);

long long regul_out_fixed(signed int e,signed int* b0);

void regul_update_fixed(signed int e,signed int* b1,signed int* a1);

#endif /* _regul_fixed_ */
