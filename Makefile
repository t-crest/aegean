TCREST_TOOL_PATH=$(CURDIR)/../local/bin
PATH:=$(PATH):$(TCREST_TOOL_PATH)

PATMOS_PATH=$(CURDIR)/../patmos/
PATMOS_SOURCE=$(PATMOS_PATH)/chisel/build/Patmos.v
PATMOS_BOOTAPP=bootable-cmp_hello

ARGO_PATH=$(CURDIR)/../t-crest-noc/
ARGO_SRC_PATH=$(ARGO_PATH)/noc/src

AEGEAN_PATH=./VHDL

POSEIDON=../poseidon/build/Poseidon
POSEIDON_CONV=java -cp ../poseidon/Converter/build/ converter.Converter

SIM_PATH=$(AEGEAN_PATH)/sim
VLIB=vlib -quiet work
VCOM=vcom -quiet -93
VLOG=vlog -quiet

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

.PHONY: schedule
.FORCE:

all: schedule compile-aegean

schedule:
	@$(POSEIDON) -m GREEDY -p ./config/bitorus2x2.xml -s ./config/aegean_sched.xml
	@$(POSEIDON_CONV) ./config/aegean_sched.xml ./config/init.h Aegean-c
	@cp ./config/init.h $(PATMOS_PATH)/c/init.h

update_hw: update_argo update_patmos

update_patmos:
	cd .. && ./misc/build.sh -u patmos

update_argo:
	cd $(ARGO_PATH) && git pull

compile-aegean: compile-config compile-patmos compile-argo
	$(WINE) $(VCOM) $(AEGEAN_PATH)/com_spm.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/noc_node.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/noc_n.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/aegean.vhd
#	$(WINE) $(VCOM) $(AEGEAN_PATH)/altera/cyc2_pll.vhd
#	$(WINE) $(VCOM) $(AEGEAN_PATH)/aegean_top_de2_70.vhd

compile-argo:
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/bram.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/bram_tdp.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/counter.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/dma.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/nAdapter.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/hpu.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/xbar.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/router.vhd
#	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/noc_node.vhd
#	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/noc_n.vhd


$(PATMOS_SOURCE): .FORCE
	make -C $(PATMOS_PATH) BOOTAPP=$(PATMOS_BOOTAPP) gen

compile-patmos: $(PATMOS_SOURCE)
	$(WINE) $(VLOG) $(PATMOS_SOURCE)

compile-config:
	$(WINE) $(VLIB)
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/config.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/ocp.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/noc_defs.vhd
	$(WINE) $(VCOM) $(ARGO_SRC_PATH)/noc_interface.vhd

compile-testbench:
	$(WINE) $(VCOM) $(AEGEAN_PATH)/packages/test.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/sim/aegean_testbench.vhd

sim: compile-testbench compile-aegean
	$(WINE) vsim -novopt -do $(SIM_PATH)/aegean.do aegean_testbench

clean:
	-rm -r work
