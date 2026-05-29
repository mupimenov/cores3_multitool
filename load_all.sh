#!/bin/bash

mpremote connect /dev/ttyACM0 cp -r app :/
mpremote connect /dev/ttyACM0 cp -r core :/
mpremote connect /dev/ttyACM0 cp -r drv :/
mpremote connect /dev/ttyACM0 cp -r lib :/
mpremote connect /dev/ttyACM0 cp main.py :/