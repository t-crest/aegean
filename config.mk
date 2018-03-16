#The audio application for the Xilinx Genesys 2 board (default)
#AUDIO_ENABLED?=1 -- not needed for xilinx
AUDIO_ENABLED?=0
AEGEAN_PLATFORM?=genesys2-audio-4cores
NOC_RECONFIG?=1
PREDIFINED_TOP_ENABLED?=1
AUDIO_APP?=default_audio_app_demo_3
FX_LIST?=FX_List
LATENCY?=latency_autogen.json

# The sdram porting experiment
#AEGEAN_PLATFORM?=default-altde2-115-9core-sdram
#PREDIFINED_TOP_ENABLED?=1
