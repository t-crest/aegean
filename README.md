About Aegean
============
Configuration framework for the T-Crest platform (Aegean)

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

Other available make targets are printed by:

    make help


![alt tag](https://github.com/t-crest/aegean/raw/master/figures/aegean.png )
