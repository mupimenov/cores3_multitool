# cores3_multitool

## Building firmware

Fetch the `lvgl_micropython`, go to its root directory and run:

```bash
python3 make.py esp32 BOARD=ESP32_GENERIC_S3 DISPLAY=all INDEV=all
```

## Flashing firmware

To use a new environment:

```bash
source ~/.espressif/python_env/idf5.5_py3.13_env/bin/activate
pip3 install mpremote # if you have not installed it yet
```

Put the device into bootloader mode by holding the reset button for about 3 seconds immediately after powering on the device.

To erase the flash:

 ```bash
python3 -m esptool --chip esp32s3 --port /dev/ttyACM0 --baud 460800 erase_flash
 ```

 To load the firmware:

 ```bash
python3 -m esptool --chip esp32s3 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x0 lvgl_micropy_ESP32_GENERIC_S3-8.bin
 ```

 Or (what the `make.py` suggests):

 ```bash
python3 -m esptool --chip esp32s3 -p /dev/ttyACM0 -b 460800 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size 8MB --flash_freq 80m --erase-all 0x0 ../lvgl_micropython/build/lvgl_micropy_ESP32_GENERIC_S3-8.bin
 ```

## Loading python files

To load all the files, type:

```bash
./load_all.sh
```