# Mopidy-SevenSegmentDisplay

[![Latest PyPI version](https://img.shields.io/pypi/v/Mopidy-SevenSegmentDisplay.svg?style=flat)](https://pypi.python.org/pypi/Mopidy-SevenSegmentDisplay/)

[![Travis-CI build status](https://travis-ci.org/JuMalIO/mopidy-sevensegmentdisplay.svg?branch=master)](https://travis-ci.org/JuMalIO/mopidy-sevensegmentdisplay)

[![Coveralls test coverage](https://coveralls.io/repos/JuMalIO/mopidy-sevensegmentdisplay/badge.svg?branch=master)](https://coveralls.io/r/JuMalIO/mopidy-sevensegmentdisplay)

A Mopidy extension for using it with seven segment display.

![](https://raw.githubusercontent.com/JuMalIO/mopidy-sevensegmentdisplay/master/sevensegmentdisplay.jpg)

| 

![](https://raw.githubusercontent.com/JuMalIO/mopidy-sevensegmentdisplay/master/sevensegmentdisplay-1.gif)

| 

![](https://raw.githubusercontent.com/JuMalIO/mopidy-sevensegmentdisplay/master/sevensegmentdisplay-2.gif)

## Installation

Install by running:

    pip install Mopidy-SevenSegmentDisplay

## Configuration

Optionally defaults can be configured in `mopidy.conf` config file (the
default default values are shown below):

    [sevensegmentdisplay]

    buttons_enabled = false
    light_sensor_enabled = true
    relay_enabled = false
    ir_receiver_enabled = true

    ir_remote = manufacturer

    default_tracks = http://janus.shoutca.st:8788/stream

    default_volume = 20
    default_preset = flat

    light_sensor_volume = 5
    light_sensor_preset = nobass
    light_sensor_time_from = 22
    light_sensor_time_to = 4

    display_min_brightness = 13
    display_max_brightness = 15
    display_off_time_from = 8
    display_off_time_to = 17

## Usage

Make sure that the [HTTP
extension](http://docs.mopidy.com/en/latest/ext/http/) is enabled. Then
browse to the app on the Mopidy server (for instance,
<http://localhost/sevensegmentdisplay/>).

## Changelog

### v0.3.1

-   Fixed timer issue on webpage

### v0.3.0

-   Timers added to webpage
-   Possibility to disable features in config
-   Music presets moved from sh to python
-   Menu animations changed
-   Light sensor added
-   Reboot/halt menu added
-   Refactoring
-   Minor adjustments

### v0.2.1

-   Refactoring release.

### v0.2.0

-   Initial release.

### v0.1.0 (UNRELEASED)

-   Initial release.
