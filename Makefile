AEGEAN_PATH?=$(CURDIR)
#AEGEAN_PLATFORM?=sync-phase
AEGEAN_PLATFORM?=mandelbrot_demo
AEGEAN_PLATFORM_FILE=$(AEGEAN_PATH)/config/$(AEGEAN_PLATFORM).xml

BUILD_PATH?=$(AEGEAN_PATH)/build/$(AEGEAN_PLATFORM)

PATMOS_PATH?=$(CURDIR)/../patmos
PATMOS_SOURCE?=$(BUILD_PATH)/*.v
PATMOS_BOOTAPP?=bootable-mandelbrot_par

AEGEAN_SRC_PATH?=$(AEGEAN_PATH)/vhdl
AEGEAN_SRC=$(patsubst %,$(BUILD_PATH)/%,\
	noc.vhd aegean.vhd)
AEGEAN_CONFIG_SRC=$(patsubst %,$(BUILD_PATH)/%,\
	config.vhd)
TEST_SRC=$(patsubst %,$(AEGEAN_SRC_PATH)/%,\
	packages/test.vhd)
MEM_SRC=$(patsubst %,$(PATMOS_PATH)/hardware/modelsim/%,\
	conversions.vhd gen_utils.vhd sim_ssram_512x36.vhd)
TESTBENCH_SRC=$(patsubst %,$(BUILD_PATH)/%,\
	aegean_testbench.vhd)

POSEIDON_PATH?=$(CURDIR)/../poseidon
POSEIDON?=$(POSEIDON_PATH)/build/Poseidon
POSEIDON_CONV=java -cp $(POSEIDON_PATH)/Converter/build/ converter.Converter


ARGO_PATH?=$(CURDIR)/../argo
ARGO_SRC_PATH?=$(ARGO_PATH)/noc/src
ARGO_SRC=$(patsubst %,$(ARGO_SRC_PATH)/%,\
	noc_defs.vhd noc_interface.vhd bram.vhd bram_tdp.vhd counter.vhd\
	dma.vhd nAdapter.vhd hpu.vhd xbar.vhd router.vhd com_spm.vhd noc_node.vhd)
CONFIG_SRC=$(patsubst %,$(ARGO_SRC_PATH)/%,\
	ocp.vhd)


SIM_PATH?=$(AEGEAN_SRC_PATH)/sim
SYNTH_PATH=$(BUILD_PATH)/quartus
VLIB=vlib -quiet work
VCOM=vcom -quiet -93 -work $(BUILD_PATH)/work
VLOG=vlog -quiet -work $(BUILD_PATH)/work
VSIM=vsim -novopt -lib $(BUILD_PATH)/work

ifeq ($(WINDIR),)
	S=:
else
	S=\;
endif

# Use Wine on OSX
# I would like to use a better way, but some shell variables
# are not set within make.... Don't know why...
ifeq ($(TERM_PROGRAM),Apple_Terminal)
	WINE=wine
else
	WINE=
endif

# Temporary file specifying the configuration of the latest platform build
PGEN=$(BUILD_PATH)/.pgen

.PHONY: sim synth config platform compile
.FORCE:

all: sim

#########################################################################
# Generation of source code for the platform described in AEGEAN_PLATFORM
# Call make platform
#########################################################################

platform: $(BUILD_PATH)/init.h

$(BUILD_PATH)/init.h: $(PGEN)

#platform: $(AEGEAN_PLATFORM_FILE) $(BUILD_PATH) quartus_files
#	python3 $(AEGEAN_PATH)/python/main.py $(AEGEAN_PLATFORM_FILE)

$(PGEN): $(AEGEAN_PLATFORM_FILE) $(BUILD_PATH) quartus_files
	@python3 $(AEGEAN_PATH)/python/main.py $(AEGEAN_PLATFORM_FILE)
	@echo $(AEGEAN_PLATFORM)+$(BUILD_PATH) > $(PGEN)

$(BUILD_PATH):
	mkdir -p $(BUILD_PATH)/xml

quartus_files: \
	$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.cdf \
	$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.qpf \
	$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.qsf \
	$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.sdc

$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.cdf: $(AEGEAN_PATH)/quartus/aegean_top.cdf
	-mkdir -p $(dir $@)
	-cp $< $@
$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.qpf: $(AEGEAN_PATH)/quartus/aegean_top.qpf
	-mkdir -p $(dir $@)
	-cp $< $@
$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.qsf: $(AEGEAN_PATH)/quartus/aegean_top.qsf
	-mkdir -p $(dir $@)
	-cp $< $@
$(BUILD_PATH)/quartus/$(AEGEAN_PLATFORM)_top.sdc: $(AEGEAN_PATH)/quartus/aegean_top.sdc
	-mkdir -p $(dir $@)
	-cp $< $@

##########################################################################
# Compilation of source code for the platform described in AEGEAN_PLATFORM
# Call make compile
##########################################################################
compile: $(BUILD_PATH)/work compile-config compile-patmos compile-argo $(AEGEAN_SRC)
	$(WINE) $(VCOM) $(AEGEAN_SRC)

$(BUILD_PATH)/work:
	mkdir -p $(BUILD_PATH)
	cd $(BUILD_PATH) && $(WINE) $(VLIB)

compile-argo: $(BUILD_PATH)/work compile-config $(ARGO_SRC)
	$(WINE) $(VCOM) $(ARGO_SRC)

#$(PATMOS_SOURCE): $(PATMOS_PATH)/c/init.h .FORCE
#	make -C $(PATMOS_PATH) BOOTAPP=$(PATMOS_BOOTAPP) BOOTBUILDDIR=$(BUILD_PATH) HWBUILDDIR=$(BUILD_PATH) gen

compile-patmos: $(BUILD_PATH)/work $(PATMOS_SOURCE)
	$(WINE) $(VLOG) $(PATMOS_SOURCE)

compile-config: $(BUILD_PATH)/work $(AEGEAN_CONFIG_SRC) $(CONFIG_SRC)
	$(WINE) $(VCOM) $(AEGEAN_CONFIG_SRC)
	$(WINE) $(VCOM) $(CONFIG_SRC)

#########################################################################
# Simulation of source code for the platform described in AEGEAN_PLATFORM
# Call make sim
#########################################################################
sim: compile $(BUILD_PATH)/work compile $(TEST_SRC) $(TESTBENCH_SRC)
	$(WINE) $(VCOM) $(TEST_SRC) $(MEM_SRC) $(TESTBENCH_SRC)
	$(WINE) $(VSIM) -do $(SIM_PATH)/aegean.do aegean_testbench

synth: $(PATMOS_SOURCE) $(CONFIG_SRC) $(ARGO_SRC) $(AEGEAN_SRC)
	quartus_map $(SYNTH_PATH)/$(AEGEAN_PLATFORM)_top
	quartus_fit $(SYNTH_PATH)/$(AEGEAN_PLATFORM)_top
	quartus_asm $(SYNTH_PATH)/$(AEGEAN_PLATFORM)_top
	quartus_sta $(SYNTH_PATH)/$(AEGEAN_PLATFORM)_top

config:
	quartus_pgm -c USB-Blaster -m JTAG $(SYNTH_PATH)/$(AEGEAN_PLATFORM)_top.cdf


update_hw: update_argo update_patmos

update_patmos:
	cd .. && ./misc/build.sh -u patmos

update_argo:
	cd $(ARGO_PATH) && git pull


clean:
	-rm -r $(BUILD_PATH)

cleanall:
	-rm -r $(AEGEAN_PATH)/build

help:
	@echo "================================================================================"
	@echo "== This is the help target of the Aegean main Makefile."
	@echo "== The variable AEGEAN_PLATFORM set the platform specification"
	@echo "== in the config directory."
	@echo "=="
	@echo "== Targets:"
	@echo "==     all        : Builds all that is needed to simulate thedescribed platform."
	@echo "=="
	@echo "==     platform   : Generates the source files for the platform described"
	@echo "==                  in AEGEAN_PLATFORM file."
	@echo "=="
	@echo "==     compile    : Compiles the full platform."
	@echo "=="
	@echo "==     sim        : Starts the simulation of the platform."
	@echo "=="
	@echo "==     synth      : Synthesises the platform."
	@echo "=="
	@echo "==     update_hw  : Updates the hardware repos."
	@echo "=="
	@echo "==     clean      : Cleans the build directory of the specified"
	@echo "==                   platform specification."
	@echo "=="
	@echo "==     cleanall   : Cleans all the build directories."
	@echo "=="
	@echo "================================================================================"
