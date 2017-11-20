prespy
======

version number: 0.0.12
author: Gavin Cooper

Overview
--------

`prespy` is a library meant to ease the use of [Presentation](http://www.neurobs.com)&reg; log files in a Python environment. It also provides a replica command line version of the SCLA (Sound Card Latency Analyser) program from the same company.

Details
-------

It contains three modules, one for reading Presentation log files, one for writing Matlab/SPM `m-file` script of fMRI event information and the final one is the recreation of the SCLA program in command line form.

Log File Reader
---------------

This exposes a simple load function to read a Presentation log file into memory and extract the relevant event information into an accessible format. The `load` function returns a `Record` object that stores metadata about the file (Subject ID for instance) as well as a lists of `Event` objects.

Each `Event` object has the full data accessible as well as shorthand attributes for event type, event code and timestamp in milliseconds.

MRI Timing
----------

This provides two functions, one to create lists of events in seconds since first pulse and the other to write a dictionary full of such values to an m-file for Matlab to read in.

SCLA Information
----------------

This module recreates the logic of the [NeurobehavioralSystems](http://www.neurobs.com/menu_presentation/menu_hardware/system_configuration) provided software, SCLA.

The use of this software relies on several things pre-existing:

* A PC running Presentation (Stimulus)
* A second PC with a sound card and sound input (Recording)
* A custom made cable

The general process to to play a sound repeated multiple time on the first PC using Presentation, whilst also sending codes via a parallel port. The first PC is connected to the second via an audio cable that has been modified to feed the audio signal and parallel port signal to the input of the sound card on the Recording computer. The modification is quite simple and involves splitting the stereo cable and joining one of the two channels to pin 2 of a parallel port.

With the logfile recorded by the Stimulus machine and the sound file recorded by the Recording machine we can compare the timing of when Presentation says it sent a sound with respect to when the Recording computer says it received them. (The parallel port code is used as a presumable fast/low jitter referece for the comparison)

Installation / Usage
--------------------

To install use pip:

    $ pip install prespy

If you have a local version you can also use:

    $ pip install <path_to_package>/prespy-0.0.12.tar.gz


To use the command line script, once installed you can run `pres-scla <soundfile> <logfile>` to analyse the difference in sound presentation times as recorded in each file.

For more information on the options you can pass to the scla command you can type in `pres-scla --help` for the full list.


Requirements
------------

The following are required by certain elements of the package and may need to
be installed separately if you are using them.

+ matplotlib (required by scla subpackage if plotting is requested)

Contributing
------------

TBD

Example
-------

TBD
