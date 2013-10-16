TCREST_TOOL_PATH?=$(CURDIR)/../local/bin
PATH:=$(PATH):$(TCREST_TOOL_PATH)

AEGEAN_PATH?=$(CURDIR)
AEGEAN_SRC_PATH?=$(AEGEAN_PATH)/VHDL
AEGEAN_SRC=$(patsubst %,$(AEGEAN_SRC_PATH)/%,\
	com_spm.vhd noc_node.vhd noc_n.vhd aegean.vhd)
TESTBENCH_SRC=$(patsubst %,$(AEGEAN_SRC_PATH)/%,\
	packages/test.vhd sim/aegean_testbench.vhd)

POSEIDON_PATH?=$(CURDIR)/../poseidon
POSEIDON?=$(POSEIDON_PATH)/build/Poseidon
POSEIDON_CONV=java -cp $(POSEIDON_PATH)/Converter/build/ converter.Converter

BUILD_PATH?=$(AEGEAN_PATH)/build

PATMOS_PATH?=$(CURDIR)/../patmos
PATMOS_SOURCE?=$(BUILD_PATH)/Patmos.v
PATMOS_BOOTAPP?=bootable-mandelbrot_par

ARGO_PATH?=$(CURDIR)/../t-crest-noc
ARGO_SRC_PATH?=$(ARGO_PATH)/noc/src
ARGO_SRC=$(patsubst %,$(ARGO_SRC_PATH)/%,\
	bram.vhd bram_tdp.vhd counter.vhd dma.vhd nAdapter.vhd hpu.vhd xbar.vhd router.vhd)
CONFIG_SRC=$(patsubst %,$(ARGO_SRC_PATH)/%,\
	config.vhd ocp.vhd noc_defs.vhd noc_interface.vhd)


SIM_PATH?=$(AEGEAN_SRC_PATH)/sim
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

.PHONY: schedule sim synth config
.FORCE:

all: sim

schedule: $(AEGEAN_PATH)/config/init.h

$(BUILD_PATH)/init.h: $(BUILD_PATH)/aegean_sched.xml
	$(POSEIDON_CONV) $< $@ Aegean-c

$(BUILD_PATH)/aegean_sched.xml: $(AEGEAN_PATH)/config/bitorus2x2.xml
	mkdir -p $(BUILD_PATH)
	$(POSEIDON) -m GREEDY -p $< -s $@

$(PATMOS_PATH)/c/init.h: $(BUILD_PATH)/init.h
	cp $< $@

update_hw: update_argo update_patmos

update_patmos:
	cd .. && ./misc/build.sh -u patmos

update_argo:
	cd $(ARGO_PATH) && git pull

$(BUILD_PATH)/work:
	mkdir -p $(BUILD_PATH)
	cd $(BUILD_PATH) && $(WINE) $(VLIB)

compile-aegean: $(BUILD_PATH)/work compile-config compile-patmos compile-argo $(AEGEAN_SRC)
	$(WINE) $(VCOM) $(AEGEAN_SRC)

compile-argo: $(BUILD_PATH)/work $(ARGO_SRC)
	$(WINE) $(VCOM) $(ARGO_SRC)

$(PATMOS_SOURCE): $(PATMOS_PATH)/c/init.h .FORCE
	make -C $(PATMOS_PATH) BOOTAPP=$(PATMOS_BOOTAPP) BOOTBUILDDIR=$(BUILD_PATH) CHISELBUILDDIR=$(BUILD_PATH) gen

compile-patmos: $(BUILD_PATH)/work $(PATMOS_SOURCE)
	$(WINE) $(VLOG) $(PATMOS_SOURCE)

compile-config: $(BUILD_PATH)/work $(CONFIG_SRC)
	$(WINE) $(VCOM) $(CONFIG_SRC)

compile-testbench: $(BUILD_PATH)/work compile-aegean $(TESTBENCH_SRC)
	$(WINE) $(VCOM) $(TESTBENCH_SRC)

sim: compile-aegean compile-testbench
	$(WINE) $(VSIM) -do $(SIM_PATH)/aegean.do aegean_testbench

synth: $(PATMOS_SOURCE) $(CONFIG_SRC) $(ARGO_SRC) $(AEGEAN_SRC)
	quartus_map quartus/aegean_top
	quartus_fit quartus/aegean_top
	quartus_asm quartus/aegean_top
	quartus_sta quartus/aegean_top

config:
	quartus_pgm -c USB-Blaster -m JTAG quartus/output_files/aegean_top.cdf

clean:
	-rm -r $(BUILD_PATH)