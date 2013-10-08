PATMOS_PATH=../patmos/patmos/chisel/build
PATMOS_SOURCE=${PATMOS_PATH}/Patmos.v
ARGO_PATH=../t-crest-noc/noc/src
AEGEAN_PATH=./VHDL
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

all:

update_hw: update_argo update_patmos

update_patmos:
	cd ../patmos && ./misc/build.sh -u patmos

update_argo:
	cd ../t-crest-noc && git pull

compile-aegean: compile-config compile-patmos compile-argo
	$(WINE) $(VCOM) $(AEGEAN_PATH)/com_spm.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/noc_node.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/noc_n.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/aegean.vhd
#	$(WINE) $(VCOM) $(AEGEAN_PATH)/altera/cyc2_pll.vhd
#	$(WINE) $(VCOM) $(AEGEAN_PATH)/aegean_top_de2_70.vhd

compile-argo:
	$(WINE) $(VCOM) $(ARGO_PATH)/bram.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/bram_tdp.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/counter.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/dma.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/nAdapter.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/hpu.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/xbar.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/router.vhd
#	$(WINE) $(VCOM) $(ARGO_PATH)/noc_node.vhd
#	$(WINE) $(VCOM) $(ARGO_PATH)/noc_n.vhd


compile-patmos:
	cd ../patmos/patmos && ./scripts/rbs_test.sh
	$(WINE) $(VLOG) ${PATMOS_SOURCE}

compile-config:
	$(WINE) $(VLIB)
	$(WINE) $(VCOM) $(ARGO_PATH)/config.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/ocp.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/noc_defs.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/noc_interface.vhd


sim: compile-aegean
	$(WINE) $(VCOM) $(AEGEAN_PATH)/packages/test.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/sim/aegean_testbench.vhd
	$(WINE) vsim -novopt -do $(SIM_PATH)/aegean.do aegean_testbench

clean:
	-rm -r work
