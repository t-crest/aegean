PATMOS_PATH=../patmos/patmos/chisel/build
PATMOS_SOURCE=${PATMOS_PATH}/Patmos.v
ARGO_PATH=../t-crest-noc/noc/src
AEGEAN_PATH=./VHDL
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

update_hw:
	cd ../patmos && ./misc/build.sh -u patmos
	cd ../t-crest-noc && git pull

compile-aegean: compile-patmos
#compile-argo
	$(WINE) $(VCOM) $(AEGEAN_PATH)/packages/config.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/packages/ocp.vhd
	$(WINE) $(VCOM) $(AEGEAN_PATH)/aegean.vhd
#	$(WINE) $(VCOM) $(AEGEAN_PATH)/altera/cyc2_pll.vhd
#	$(WINE) $(VCOM) $(AEGEAN_PATH)/aegean_top_de2_70.vhd

compile-argo:
	$(WINE) $(VCOM) $(ARGO_PATH)/defs.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/bram.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/bram_tdp.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/counter.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/dma.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/nAdapter.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/hpu.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/xbar.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/router.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/noc_node.vhd
	$(WINE) $(VCOM) $(ARGO_PATH)/noc_n.vhd


compile-patmos:
	$(WINE) $(VLIB)
	$(WINE) $(VLOG) ${PATMOS_SOURCE}

sim:
	$(WINE) vsim aegean
