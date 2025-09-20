# LVGL for MicroBlocks

This is a work-in-progress project where LVGL is added to the Microblocks VM.

## Firmware
in the directory `lvgl_vm/firmware` we store the single file firmware images. Easy to upload using [ESPTool online flashing util](https://espressif.github.io/esptool-js/). Connect, set `flash Address` to 0x0 and select firmware. Hit program (disconnect from MicroBlocks IDE first).

## Microblocks code
in the `lvgl_mb/microblocks` directory the latest version of the `lvgl.ubl` library and example and demo program code can be found.

