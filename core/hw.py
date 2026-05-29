from micropython import const
import machine
import network
import lcd_bus
import time
import ntptime

import i2c
import ft6x36

import drv.axp2101
import drv.pcf8563
import drv.aw9523
import drv.ili9342

import lvgl as lv

import lib.xtime

_I2C_SYS_SDA = const(12)
_I2C_SYS_SCL = const(11)

_MISO_PIN = const(35)
_SCLK_PIN = const(36)
_MOSI_PIN = const(37)
_CS_PIN = const(3)

_DC_PIN = const(35)  # same as MISO
_FREQ = const(40000000)

_WIFI_SSID = const("CU_cYp2")
_WIFI_PASSWD = const("2gc7n2m7")

DISPLAY_WIDTH = const(320)
DISPLAY_HEIGHT = const(240)

i2c_bus = None

axp2101: drv.axp2101.AXP2101 | None = None

rtc = None
ext_rtc = None

ioexp = None

disp_rst = None
touch_rst = None

spi_bus = None
display_bus = None

display = None

touch_dev = None

indev = None

wlan: network.WLAN | None = None


def pmicOnline(axp2101: drv.axp2101.AXP2101):
    id = axp2101.getChipID()
    return id == drv.axp2101.XPOWERS_AXP2101_CHIP_ID


def pmicPrintInfo(axp2101: drv.axp2101.AXP2101):
    print("Battery voltage:", axp2101.getBattVoltage())
    print("Temperature:", axp2101.getTemperature())

    print("DC1 enabled:", axp2101.isEnableDC1())
    print("DC1 voltage:", axp2101.getDC1Voltage())
    print("DC2 enabled:", axp2101.isEnableDC2())
    print("DC2 voltage:", axp2101.getDC2Voltage())
    print("DC3 enabled:", axp2101.isEnableDC3())
    print("DC3 voltage:", axp2101.getDC3Voltage())
    print("DC4 enabled:", axp2101.isEnableDC4())
    print("DC4 voltage:", axp2101.getDC4Voltage())
    print("DC5 enabled:", axp2101.isEnableDC5())
    print("DC5 voltage:", axp2101.getDC5Voltage())

    print("ALDO1 enabled:", axp2101.isEnableALDO1())
    print("ALDO1 voltage:", axp2101.getALDO1Voltage())
    print("ALDO2 enabled:", axp2101.isEnableALDO2())
    print("ALDO2 voltage:", axp2101.getALDO2Voltage())
    print("ALDO3 enabled:", axp2101.isEnableALDO3())
    print("ALDO3 voltage:", axp2101.getALDO3Voltage())
    print("ALDO4 enabled:", axp2101.isEnableALDO4())
    print("ALDO4 voltage:", axp2101.getALDO4Voltage())

    print("BLDO1 enabled:", axp2101.isEnableBLDO1())
    print("BLDO1 voltage:", axp2101.getBLDO1Voltage())
    print("BLDO2 enabled:", axp2101.isEnableBLDO2())
    print("BLDO2 voltage:", axp2101.getBLDO2Voltage())

    print("DLDO1 enabled (BL):", axp2101.isEnableDLDO1())
    print("DLDO1 voltage (BL):", axp2101.getDLDO1Voltage())
    print("DLDO2 enabled:", axp2101.isEnableDLDO2())
    print("DLDO2 voltage:", axp2101.getDLDO2Voltage())


def connect_wifi(timeout: int = 10) -> bool:
    global wlan

    if wlan and not wlan.isconnected():
        wlan.connect(_WIFI_SSID, _WIFI_PASSWD)
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan and wlan.isconnected():
        return True
    return False


def sync_time(timeout: int = 2) -> bool:
    global rtc
    global ext_rtc
    global wlan

    if wlan and wlan.isconnected():
        try:
            ntptime.timeout = timeout
            t = ntptime.time()
            tm = time.gmtime(t)
            rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))  # ty:ignore[unresolved-attribute]
            ext_rtc.datetime((tm[0], tm[1], tm[2], tm[3], tm[4], tm[5], tm[6]))  # ty:ignore[unresolved-attribute]
            return True
        except Exception:
            pass
    return False


def init():
    global axp2101
    global i2c_bus
    global rtc
    global ext_rtc
    global ioexp
    global spi_bus
    global display_bus
    global display
    global touch_dev
    global indev
    global wlan

    print("HW init started")

    i2c_bus = i2c.I2C.Bus(host=0, scl=_I2C_SYS_SCL, sda=_I2C_SYS_SDA)

    # IO expander
    ioexp = drv.aw9523.AW9523(i2c_bus, 0x58)

    usb_otg_en = drv.aw9523.Pin(5, mode=machine.Pin.OUT)
    usb_otg_en.off()  # Turns on by 0

    bus_out_en = drv.aw9523.Pin(1, mode=machine.Pin.OUT)
    bus_out_en.on()  # Turns off by 1

    boost_en = drv.aw9523.Pin(15, mode=machine.Pin.OUT)
    boost_en.on()  # Turns off by 1

    disp_rst = drv.aw9523.Pin(9, mode=machine.Pin.OUT)
    disp_rst.on()

    touch_rst = drv.aw9523.Pin(0, mode=machine.Pin.OUT)
    touch_rst.on()

    # PMIC
    axp2101 = drv.axp2101.AXP2101(i2c_bus=i2c_bus)
    if not pmicOnline(axp2101):
        raise Exception("PMIC is offline")

    axp2101.setDLDO1Voltage(3000)
    axp2101.enableDLDO1()
    axp2101.setChargingLedMode(axp2101.XPOWERS_CHG_LED_CTRL_CHG)
    axp2101.setPrechargeCurr(axp2101.XPOWERS_AXP2101_PRECHARGE_100MA)
    axp2101.setChargerConstantCurr(axp2101.XPOWERS_AXP2101_CHG_CUR_200MA)
    axp2101.setChargerTerminationCurr(axp2101.XPOWERS_AXP2101_CHG_ITERM_25MA)
    axp2101.setChargeTargetVoltage(axp2101.XPOWERS_AXP2101_CHG_VOL_4V2)
    axp2101.enableBattDetection()
    axp2101.enableCellbatteryCharge()
    axp2101.enableSystemVoltageMeasure()
    axp2101.enableVbusVoltageMeasure()

    rtc = machine.RTC()  # ty:ignore[no-matching-overload]
    ext_rtc = drv.pcf8563.PCF8563(i2c_bus)

    dt = ext_rtc.datetime()
    print("Boot RTC time (UTC):", lib.xtime.datetime_to_string(dt, True))
    rtc.datetime((dt[0], dt[1], dt[2], dt[6], dt[3], dt[4], dt[5], 0))  # ty:ignore[unresolved-attribute]
    print("Boot device time:", lib.xtime.datetime_to_string(lib.xtime.localtimez()))

    spi_bus = machine.SPI.Bus(
        host=2,
        mosi=_MOSI_PIN,
        miso=_MISO_PIN,
        sck=_SCLK_PIN,
    )

    display_bus = lcd_bus.SPIBus(
        spi_bus=spi_bus,
        dc=_DC_PIN,
        freq=_FREQ,
        cs=_CS_PIN,
    )

    display = drv.ili9342.ILI9342(
        data_bus=display_bus,
        display_width=DISPLAY_WIDTH,
        display_height=DISPLAY_HEIGHT,
        frame_buffer1=None,
        frame_buffer2=None,
        reset_pin=disp_rst,
        reset_state=drv.ili9342.STATE_HIGH,
        power_pin=None,
        power_on_state=drv.ili9342.STATE_HIGH,
        backlight_pin=None,
        backlight_on_state=drv.ili9342.STATE_HIGH,
        offset_x=0,
        offset_y=0,
        color_space=lv.COLOR_FORMAT.RGB565,
        rgb565_byte_swap=True,
    )

    display.init()
    display.set_backlight(100)
    display.set_color_inversion(True)

    touch_dev = i2c.I2C.Device(
        bus=i2c_bus, dev_id=ft6x36.I2C_ADDR, reg_bits=ft6x36.BITS
    )

    indev = ft6x36.FT6x36(touch_dev)

    # if not indev.is_calibrated:
    #   indev.calibrate()
    # indev._cal.reset()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print("HW init finished")


def get_pmic():
    return axp2101


def calibrate_touch():
    global indev

    if indev:
        indev.calibrate()
