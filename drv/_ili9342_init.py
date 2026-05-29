# Copyright (c) 2024 - 2025 Kevin G. Schlosser

import time
import lvgl as lv


def init(self):
    param_buf = bytearray(15)
    param_mv = memoryview(param_buf)

    param_buf[:3] = bytearray([0xFF, 0x93, 0x42])
    self.set_params(0xC8, param_mv[:3])  # SETEXTC

    param_buf[:2] = bytearray([0x12, 0x12])
    self.set_params(0xC0, param_mv[:2])  # PWCTR1

    param_buf[:1] = bytearray([0x03])
    self.set_params(0xC1, param_mv[:1])  # PWCTR2

    param_buf[:1] = bytearray([0xF2])
    self.set_params(0xC5, param_mv[:1])  # VMCTR1

    param_buf[:1] = bytearray([0xE0])
    self.set_params(0xB0, param_mv[:1])  # IFMODE

    param_buf[:3] = bytearray([0x01, 0x00, 0x00])
    self.set_params(0xF6, param_mv[:3])  # IFCTL

    param_buf[:15] = bytearray(
        [
            0x00,
            0x0C,
            0x11,
            0x04,
            0x11,
            0x08,
            0x37,
            0x89,
            0x4C,
            0x06,
            0x0C,
            0x0A,
            0x2E,
            0x34,
            0x0F,
        ]
    )
    self.set_params(0xE0, param_mv[:15])  # GMCTRP1

    param_buf[:15] = bytearray(
        [
            0x00,
            0x0B,
            0x11,
            0x05,
            0x13,
            0x09,
            0x33,
            0x67,
            0x48,
            0x07,
            0x0E,
            0x0B,
            0x2E,
            0x33,
            0x0F,
        ]
    )
    self.set_params(0xE1, param_mv[:15])  # GMCTRN1

    param_buf[:4] = bytearray([0x08, 0x82, 0x1D, 0x04])
    self.set_params(0xB6, param_mv[:4])  # DFUNCTR

    self.set_params(0x38)  # IDMOFF

    param_buf[0] = self._madctl(
        self._color_byte_order,
        self._ORIENTATION_TABLE,
    )
    self.set_params(0x36, param_mv[:1])  # MADCTL

    color_size = lv.color_format_get_size(self._color_space)
    if color_size == 2:
        pixel_format = 0x55
    else:
        raise RuntimeError(
            f"{self.__class__.__name__} IC only supports lv.COLOR_FORMAT.RGB565"
        )

    param_buf[0] = pixel_format
    self.set_params(0x3A, param_mv[:1])  # COLMOD
    
    self.set_params(0x29)  # DISPON
    time.sleep_ms(20)  # ty:ignore[unresolved-attribute]

    self.set_params(0x11)  # SLPOUT
    time.sleep_ms(120)  # ty:ignore[unresolved-attribute]

    print("ILI9342 configured")
