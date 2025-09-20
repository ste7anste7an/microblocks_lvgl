# LVGL for MicroBlocks

This is a work-in-progress project where LVGL is added to the Microblocks VM.

## Compiling

You can compile LVGL capable MicroBlocks VM for platforms:
- having an ESP32
- having PSRAM available
- having a working TFT screen in MicroBlocks


Change the environment, or copy an existing environment in the `platformio.ini` ad add:
- `-Ivm -D LVGL -DLV_CONF_INCLUDE_SIMPLE` to the `build_flags
- `lvgl/lvgl@^9.2.2` to the `lib_deps`

## Firmware
in the directory `lvgl_vm/firmware` we store the single file firmware images. Easy to upload using [ESPTool online flashing util](https://espressif.github.io/esptool-js/). Connect, set `flash Address` to 0x0 and select firmware. Hit program (disconnect from MicroBlocks IDE first).

## Microblocks code
in the `lvgl_mb/microblocks` directory the latest version of the `lvgl.ubl` library and `lvgl.ubp` program code can be found.

## Memory usage

To limit DRAM usage, PSRAM is used for storing the array 
`uint16_t bufferPixels[BUFFER_PIXELS_SIZE];` in `tftPrims.cpp`. That is now stores in PSRAM using: 

```__attribute__((section(".ext_ram"))) uint16_t bufferPixels[BUFFER_PIXELS_SIZE];```

Furthermore, using the `-DLV_CONF_INCLUDE_SIMPLE` build_flag in platformio.ini, the LV_MEM is defined in PSRAM as well.
