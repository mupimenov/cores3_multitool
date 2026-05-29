import lvgl as lv

from core.ui import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, VIEWPORT_OFFX, VIEWPORT_OFFY
from core.app import BasicApp

from core.hw import get_pmic
from drv.axp2101 import AXP2101


class BatStatusApp(BasicApp):
    def __init__(self):
        self.screen = lv.obj(None)  # ty:ignore[invalid-argument-type]

        stack = lv.obj(self.screen)
        stack.set_size(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        stack.set_pos(VIEWPORT_OFFX, VIEWPORT_OFFY)

        stack.set_layout(lv.LAYOUT.FLEX)
        stack.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        stack.set_flex_align(
            lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.START
        )

        stack.set_style_pad_column(10, 0)
        stack.set_style_pad_all(5, 0)

        self.volt_lbl = lv.label(stack)
        self.volt_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.volt_lbl.set_width(lv.pct(90))

        self.vbus_lbl = lv.label(stack)
        self.vbus_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.vbus_lbl.set_width(lv.pct(90))

        self.temp_lbl = lv.label(stack)
        self.temp_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.temp_lbl.set_width(lv.pct(90))

        lv.timer_create(
            lambda tobj: self._update_status(),
            1000,
            None,
        )

        self._update_status()

    def __del__(self):
        if self.screen:
            self.screen.delete()

    def _update_status(self):
        pmic: AXP2101 = get_pmic()
        self.volt_lbl.set_text(
            f"Battery voltage: {pmic.getBattVoltage() / 1000.0: .2f} V"
        )
        vbus_v = pmic.getVbusVoltage() / 1000.0
        vbus_v_str = f"{vbus_v: .2f}" if vbus_v < 6.0 else "-"
        self.vbus_lbl.set_text(
            f"VBUS: {vbus_v_str} V, VSYS: {pmic.getSystemVoltage() / 1000.0: .2f} V"
        )
        self.temp_lbl.set_text(f"PMIC temperature: {pmic.getTemperature(): .1f} C")

    def show(self):
        if self.screen:
            lv.screen_load(self.screen)

    def standby(self):
        pass

    def resume(self):
        pass
