![Logos](doc/Logos.svg)

# MonVerifyTools

A set of scripts to automatically check the content of periodically obtained measurement data files, useful for larger monitoring projects.

## Motivation

Engineering/scientific monitoring typically starts small with a few sensors that can be read and analyzed by users in suitable intervals. 
As soon as number of sensors increases, and measurement frequency is higher (semi-hourly or minutely values), retrieving and *checking* those monitoring values becomes a cumbersome and error-prone process.

Here, the MonVerifyTools step in and assist with automated functionality to:

- push-type collection of monitoring data files from external sources (clients)
- check for correct input format of measurement files (as expected)
- perform a set of configured content checks to see if files are complete and valid (e.g. guard against sensor fault, missing time points, broken client/server connections and partial file commits etc.)
- perform additional physical value checks (e.g. out-of-value-range checks, large oszillation/gradient checks, etc.), that signal that something might be wrong with a) sensor, b) monitored system/equipment
- log results of checks to log files for easy screening by human-users
- move offending files to separate review directory, and move correct files to "ready for processing" directories

Basically, you can think of the *MonVerifyTools* as a quality assurance interim step, between *raw data collection* and *actual data processing* (import into monitoring software, run scripts or even just dump it into LibreOffice or Excel).

![Overview](doc/Overview.png)

## How?

For now, see [documentation](doc/MonVerifyTools_Dokumentation.pdf) (currently only in German, but source code is documented in english).

