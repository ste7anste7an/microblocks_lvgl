# LVGL for MicroBlocks

This is the MicroBlocks library that implements LVGL. An LVGL capable MicroBlocks firmware is needed in order to get it working.

## Firmware for CYD
For the Cheap Yellow Display boards a generic firmware is developed. This firmware uses a configuration file that it loads from the internal filesystem of the board to configure the TFT Display and Touch controller at runtime. For a number of versions of the CYD these config files are available in the [CYD-MicroBlocks-LVGL git repo](https://github.com/ste7anste7an/CYD-MicroBlocks-LVGL).

The firmware can be downloaded from [firmware.ste7an.nl](https://firmware.ste7an.nl). Keep in mind, that when the firmware is installed for the first time, nothing appears on the screen until the correct config.txt is uploaded to the boards filesystem. 

## Microblocks library
In the `library` directory the main LVGL library `lvgl.ubl` can be found.

## Examples
The `example` directory contains a number of examples showing the possibilities with the LVGL library.

