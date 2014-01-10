#
# Copyright Technical University of Denmark. All rights reserved.
# This file is part of the T-CREST project.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of the copyright holder.
#
###############################################################################
# Authors:
#    Rasmus Bo Soerensen (rasmus@rbscloud.dk)
#
###############################################################################

import os

class Paths(object):
    """docstring for Paths"""
    def __init__(self, projectname):
        self.projectname = projectname

        self.AEGEAN_PATH = os.getcwd()

        self.XMLSCHEME = self.AEGEAN_PATH + '/xmlNotes/Aegean.xsd'

        self.ARGO_PATH = self.AEGEAN_PATH + '/../argo'
        self.POSEIDON_PATH = self.AEGEAN_PATH + '/../local/bin'
        self.POSEIDON_CONV = self.POSEIDON_PATH + '/poseidon_converter.sh'
        self.POSEIDON = self.POSEIDON_PATH + '/Poseidon'

        self.PATMOS_PATH = self.AEGEAN_PATH + '/../patmos'
        self.PATMOSHW_PATH = self.PATMOS_PATH + '/hardware'
        self.BUILD_PATH = self.AEGEAN_PATH + '/build/' + str(projectname)
        self.TMP_BUILD_PATH = self.BUILD_PATH + '/xml'

        ###################################################
        # Intermediate files
        self.GEN_PLAT = self.TMP_BUILD_PATH + '/plat.xml'
        self.GEN_COM = self.TMP_BUILD_PATH + '/com.xml'
        self.GEN_SCHED = self.TMP_BUILD_PATH + '/sched.xml'
        # The main mem should be set at some point, for now it is none
        #self.MAIN_MEM = self.BUILD_PATH + '/main_mem.dat'
        self.MAIN_MEM = 'none'

        ###################################################
        # Final config files
        self.CSCHED = self.BUILD_PATH + '/init.h'
        self.NOCFile = self.BUILD_PATH + '/noc.vhd'
        self.AegeanFile = self.BUILD_PATH + '/aegean.vhd'
        self.TopFile = self.BUILD_PATH + '/top.vhd'
        self.TestFile = self.BUILD_PATH + '/aegean_testbench.vhd'
        self.ConfFile = self.BUILD_PATH + '/config.vhd'
        self.QUARTUS_FILE = self.BUILD_PATH + '/quartus/'+str(projectname)+'_top.qsf'
