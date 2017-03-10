##############################################################
# Main makefile for the Aegean repo.
# From the Aegean repo you can build a multicore patmos
# system with an argo NoC.
##############################################################
# Copyright:
# 	DTU, BSD License
# Authors:
# 	Wolfgang Puffitsch
# 	Rasmus Bo Sorensen
##############################################################
# Include user makefile for local configurations
-include config.mk
# The project being build when calling
# "make platform|compile|sim|synth|config"
AEGEAN_PLATFORM?=default-altde2-115
# Tests to be run by buildbot
BUILDBOT_TESTS?=corethread_test test_cmp libctest
# Aegean path names
AEGEAN_PATH?=$(CURDIR)
AEGEAN_PLATFORM_FILE=$(AEGEAN_PATH)/config/$(AEGEAN_PLATFORM).xml

BUILD_PATH?=$(AEGEAN_PATH)/build/$(AEGEAN_PLATFORM)

#For BUILDING AUDIO PLATFORM (default disabled):
AUDIO_ENABLED?=0

#AUDIO FILES:
AUDIO_APP?=default_audio_app
FX_LIST?=FX_List
LATENCY?=latency_autogen.json
AUDIO_APP_FILE=$(AEGEAN_PATH)/audio_apps/$(AUDIO_APP).json
FX_LIST_FILE=$(AEGEAN_PATH)/audio_apps/$(FX_LIST).json
LATENCY_FILE=$(AEGEAN_PATH)/audio_apps/$(LATENCY)
#NoC Reconfiguration (for AUDIO): 1=Enabled, 2=Disabled
NOC_RECONFIG?=0
#destination for auto-generated NoC schedule (for AUDIO)
AEGEAN_NOCSCHED?=default-altde2-115-audio-nocsched
AEGEAN_NOCSCHED_FILE=$(AEGEAN_PATH)/config/$(AEGEAN_NOCSCHED).xml
#if NoC reconfiguration is disabled, all2all schedule for NoC (for AUDIO)
AEGEAN_NOCSCHED_FILE_ALL2ALL=$(CURDIR)/config/default-altde2-115-audio-nocsched-all2all.xml
BUILD_NOCSCHED_PATH?=$(AEGEAN_PATH)/build/$(AEGEAN_NOCSCHED)

#Use predefined top-level
PREDIFINED_TOP_ENABLED?=0

# Source file variables
PATMOS_PATH?=$(CURDIR)/../patmos
ARGO_PATH?=$(CURDIR)/../argo

AEGEAN_SRC_PATH?=$(AEGEAN_PATH)/vhdl
AEGEAN_SRC=$(patsubst %,$(BUILD_PATH)/%,\
	noc.vhd aegean.vhd)

TEST_SRC=$(patsubst %,$(AEGEAN_SRC_PATH)/%,\
	packages/test.vhd sim/pll.vhd)
MEM_SRC=$(patsubst %,$(PATMOS_PATH)/hardware/modelsim/%,\
	conversions.vhd gen_utils.vhd sim_ssram_512x36.vhd \
	CY7C10612DV33/package_timing.vhd \
	CY7C10612DV33/package_utility.vhd \
	CY7C10612DV33/cy7c10612dv33.vhd)
TESTBENCH_SRC=$(patsubst %,$(BUILD_PATH)/%,\
	aegean_top.vhd aegean_testbench.vhd)

# Tool paths
SIM_PATH?=$(AEGEAN_SRC_PATH)/sim
SYNTH_PATH=$(BUILD_PATH)/quartus
SYNTH_PATH_XILINX=$(BUILD_PATH)/ise
VLIB=vlib -quiet work
VCOM?=vcom -quiet -93 -work $(BUILD_PATH)/work
VCOM08?=vcom -quiet -2008 -work $(BUILD_PATH)/work
VLOG?=vlog -quiet -work $(BUILD_PATH)/work
VSIM?=vsim -novopt -lib $(BUILD_PATH)/work

ifeq ($(WINDIR),)
	S=:
else
	S=\;
endif

# mainly for OS X: try to use wine if modelsim is not in path...
VCOM_AVAILABLE := $(shell which vcom 2> /dev/null; echo $$?)
ifeq ($(VCOM_AVAILABLE), 1)
	PREFIX=wine
else
	PREFIX=
endif

# Temporary file specifying the configuration of the latest platform build
PGEN=$(BUILD_PATH)/.pgen
ARGO_SRC=$(BUILD_PATH)/.argo_src
VLOG_SRC=$(BUILD_PATH)/.vlog_src

.PHONY: sim synth config platform compile buildbot-test
.FORCE:

all: platform

#########################################################################
# Generation of source code for the platform described in AEGEAN_PLATFORM
# Call make platform
#########################################################################
projectname:
	@echo "Current project name:"
	@echo $(AEGEAN_PLATFORM)

audio-app-name:
	@echo "Current Audio APP name":
	@echo $(AUDIO_APP)

audio-setup: clean-noc-sched audio-generate noc-sched audio-latency

audio-generate: $(AUDIO_APP_FILE)
	@python3 $(AEGEAN_PATH)/python/audioFXGen.py $(FX_LIST_FILE) $(AUDIO_APP_FILE) $(AEGEAN_NOCSCHED_FILE) $(NOC_RECONFIG) $(LATENCY_FILE)

audio-latency: $(LATENCY_FILE)
ifeq ($(NOC_RECONFIG),1)
	@python3 $(AEGEAN_PATH)/python/audioLatencyCalc.py $(LATENCY_FILE) $(NOC_RECONFIG) $(AEGEAN_NOCSCHED_FILE)
else
	@python3 $(AEGEAN_PATH)/python/audioLatencyCalc.py $(LATENCY_FILE) $(NOC_RECONFIG) $(AEGEAN_NOCSCHED_FILE_ALL2ALL)
endif

noc-sched-name:
	@echo "Current NoC scheduling topoligy:"
	@echo $(AEGEAN_NOCSCHED)

noc-sched: $(AEGEAN_NOCSCHED_FILE_USED) $(BUILD_NOCSCHED_PATH)
ifeq ($(NOC_RECONFIG),1)
	@echo "GENERATING nocinit.c FILE FROM NoC TDM SCHEDULE"
	@echo "NoC schedule file: "
	@echo $(AEGEAN_NOCSCHED_FILE)
	@python3 $(AEGEAN_PATH)/python/nocSchedMain.py $(AEGEAN_NOCSCHED_FILE)
else
	@echo "GENERATING nocinit.c FILE FROM NoC TDM SCHEDULE"
	@echo "NoC schedule file: "
	@echo $(AEGEAN_NOCSCHED_FILE_ALL2ALL)
	@python3 $(AEGEAN_PATH)/python/nocSchedMain.py $(AEGEAN_NOCSCHED_FILE_ALL2ALL)
endif

$(BUILD_NOCSCHED_PATH):
	mkdir -p $(BUILD_NOCSCHED_PATH)/xml

platform: $(BUILD_PATH)/nocinit.c

$(BUILD_PATH)/nocinit.c: $(PGEN)

$(PGEN): $(AEGEAN_PLATFORM_FILE) $(BUILD_PATH) quartus_files ise_files
	@python3 $(AEGEAN_PATH)/python/main.py $(AEGEAN_PLATFORM_FILE) $(AUDIO_ENABLED)
	@echo $(AEGEAN_PLATFORM)+$(BUILD_PATH) > $(PGEN)
ifeq ($(PREDIFINED_TOP_ENABLED),1)
	@echo "Using predifined top level."
	cp -v -r $(AEGEAN_SRC_PATH)/top/$(AEGEAN_PLATFORM)/. $(BUILD_PATH)/
endif

$(BUILD_PATH):
	mkdir -p $(BUILD_PATH)/xml

quartus_files: \
	$(BUILD_PATH)/quartus/aegean_top.cdf \
	$(BUILD_PATH)/quartus/aegean_top.qpf \
	$(BUILD_PATH)/quartus/aegean_top.qsf \
	$(BUILD_PATH)/quartus/aegean_top.sdc

$(BUILD_PATH)/quartus/aegean_top.cdf: $(AEGEAN_PATH)/quartus/aegean_top.cdf
	-mkdir -p $(dir $@)
	-cp $< $@
$(BUILD_PATH)/quartus/aegean_top.qpf: $(AEGEAN_PATH)/quartus/aegean_top.qpf
	-mkdir -p $(dir $@)
	-cp $< $@
$(BUILD_PATH)/quartus/aegean_top.qsf: $(AEGEAN_PATH)/quartus/aegean_top.qsf
	-mkdir -p $(dir $@)
	-cp $< $@
$(BUILD_PATH)/quartus/aegean_top.sdc: $(AEGEAN_PATH)/quartus/aegean_top.sdc
	-mkdir -p $(dir $@)
	-cp $< $@

ise_files: \
	$(SYNTH_PATH_XILINX)/$(AEGEAN_PLATFORM)_sync.xise \
	$(SYNTH_PATH_XILINX)/ml605_sync.ucf \
	$(SYNTH_PATH_XILINX)/ml605_async.ucf \
	$(SYNTH_PATH_XILINX)/$(AEGEAN_PLATFORM)_async.xise

$(SYNTH_PATH_XILINX)/$(AEGEAN_PLATFORM)_sync.xise: $(AEGEAN_PATH)/ise/ml605oc_sync.xise
	-mkdir -p $(dir $@)
	-cp $< $@
$(SYNTH_PATH_XILINX)/ml605_sync.ucf: $(AEGEAN_PATH)/ise/ml605_sync.ucf
	-mkdir -p $(dir $@)
	-cp $< $@
$(SYNTH_PATH_XILINX)/ml605_async.ucf: $(AEGEAN_PATH)/ise/ml605_async.ucf
	-mkdir -p $(dir $@)
	-cp $< $@
$(SYNTH_PATH_XILINX)/$(AEGEAN_PLATFORM)_async.xise: $(AEGEAN_PATH)/ise/ml605oc_async.xise
	-mkdir -p $(dir $@)
	-cp $< $@

##########################################################################
# Compilation of source code for the platform described in AEGEAN_PLATFORM
# Call make compile
##########################################################################
compile: $(BUILD_PATH)/work compile-argo compile-vlog  $(AEGEAN_SRC)
	$(PREFIX) $(VCOM) $(AEGEAN_SRC)

$(BUILD_PATH)/work:
	mkdir -p $(BUILD_PATH)
	cd $(BUILD_PATH) && $(PREFIX) $(VLIB)

compile-argo: $(BUILD_PATH)/work $(shell cat $(ARGO_SRC)) $(ARGO_SRC)
	$(PREFIX) $(VCOM08) $(shell cat $(ARGO_SRC))

compile-vlog: $(BUILD_PATH)/work $(shell cat $(VLOG_SRC)) $(VLOG_SRC)
	$(PREFIX) $(VLOG) $(shell cat $(VLOG_SRC))

#########################################################################
# Map Xilinx libraries
#########################################################################
map-xilinx-libs:
	vmap secureip $(SECUREIPPATH)/secureip
	vmap unisim $(UNISIMPATH)/unisim

#########################################################################
# Simulation of source code for the platform described in AEGEAN_PLATFORM
# Call make sim
#########################################################################
sim: compile $(BUILD_PATH)/work $(TEST_SRC) $(TESTBENCH_SRC)
	$(PREFIX) $(VCOM) $(TEST_SRC) $(MEM_SRC) $(TESTBENCH_SRC)
	$(PREFIX) $(VSIM) -do $(SIM_PATH)/aegean.do aegean_testbench

sim-fpga: map-xilinx-libs compile $(BUILD_PATH)/work compile $(TEST_SRC) $(TESTBENCH_SRC)
	$(PREFIX) $(VCOM) $(TEST_SRC) $(MEM_SRC) $(TESTBENCH_SRC)
	$(PREFIX) $(VSIM) -do $(SIM_PATH)/aegean.do aegean_testbench

synth: $(PATMOS_SOURCE) $(CONFIG_SRC) $(shell cat $(ARGO_SRC)) $(AEGEAN_SRC) $(ARGO_SRC)
	quartus_map $(SYNTH_PATH)/aegean_top --verilog_macro="SYNTHESIS"
	quartus_fit $(SYNTH_PATH)/aegean_top
	quartus_asm $(SYNTH_PATH)/aegean_top
	quartus_sta $(SYNTH_PATH)/aegean_top

config:
	quartus_pgm -c USB-Blaster -m JTAG $(SYNTH_PATH)/aegean_top.cdf

clean-noc-sched:
	-rm -rf $(BUILD_NOCSCHED_PATH)

clean:
	-rm -rf $(BUILD_PATH)

cleanall:
	-rm -rf $(AEGEAN_PATH)/build

test:
	for test in $(BUILDBOT_TESTS); \
	do \
	 	make -C ../patmos APP=$$test comp ; \
	 	quartus_pgm -c USB-Blaster -m JTAG $(SYNTH_PATH)/aegean_top.cdf ; \
	 	patserdow -v /dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A700aiK5-if00-port0 ../patmos/tmp/$$test.elf ; \
	done

buildbot-test: clean platform compile synth test



help:
	@echo "================================================================================"
	@echo "== This is the help target of the Aegean main Makefile."
	@echo "== The variable AEGEAN_PLATFORM set the platform specification"
	@echo "== in the config directory."
	@echo "=="
	@echo "== Targets:"
	@echo "==     all        : Builds all that is needed to simulate the"
	@echo "==                   described platform."
	@echo "=="
	@echo "==     platform   : Generates the source files for the platform described"
	@echo "==                   in AEGEAN_PLATFORM file."
	@echo "=="
	@echo "==     audio-setup : Generates the NoC TDM scheduling XML file and the"
	@echo "==                    audioinit.c file first. Then, it generates the"
	@echo "== 	 	     nocinit.c file from the NoCschedule."
	@echo "=="
	@echo "==     compile    : Compiles the full platform."
	@echo "=="
	@echo "==     sim        : Starts the simulation of the platform."
	@echo "=="
	@echo "==     synth      : Synthesises the platform."
	@echo "=="
	@echo "==     clean      : Cleans the build directory of the specified"
	@echo "==                   platform specification."
	@echo "=="
	@echo "==     cleanall   : Cleans all the build directories."
	@echo "=="
	@echo "================================================================================"
