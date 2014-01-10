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

