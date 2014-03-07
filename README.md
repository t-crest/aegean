About Aegean
============
Configuration framework for the T-CREST platform (Aegean)

Aegean is a collection of Python scripts that generates an instance of the time-predictable multicore platform. The configuration of a given platform is described in XML files. Some example XML files containing platform configurations are placed in the config/ directory.


Getting started
===============
As Aegean is part of the T-CREST tool chain it is downloaded and setup through the patmos-misc/build.sh (Also described in the patmos README.md)

An additional prerequisite is python3

Generating a platform
=====================
The default platform is generated with a simple:

    make platform

To compile the generated platform:

    make compile
    
If you have a version of ModelSim supporting mixed language simulations you can simulate the generated platform by:

    make sim

Synthesize the platform for an FPGA:

    make synth

Other available make targets are printed by:

    make help


![alt tag](https://github.com/t-crest/aegean/raw/master/figures/aegean.png )


Pending changes in the Cleanup branch
=====================================

- Move bootapp option from xmlpath:/aegean/platform/IPCores/IPCore/patmos/bootrom;app to xmlpath:/aegean/platform/nodes/node;bootapp
- Remove xmlpath:/aegean/platform/topology;routerDepth
- Structure the generation of files into following categories:
	- Board specific files
	- Platform specific files
	- Software config files (nocinit.c, linker script)