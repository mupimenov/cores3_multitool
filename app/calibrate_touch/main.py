import lvgl as lv

from core.ui import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, VIEWPORT_OFFX, VIEWPORT_OFFY
from core.app import BasicApp
from core.hw import calibrate_touch


class CalibTouchApp(BasicApp):
    def __init__(self):
        self.screen = lv.obj(None)  # ty:ignore[invalid-argument-type]

        stack = lv.obj(self.screen)
        stack.set_size(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        stack.set_pos(VIEWPORT_OFFX, VIEWPORT_OFFY)

        self.calibrate_btn = lv.button(stack)
        self.calibrate_btn.align(lv.ALIGN.CENTER, 0, 0)
        self.calibrate_btn_txt = lv.label(self.calibrate_btn)
        self.calibrate_btn_txt.set_text("Calibrate")

        self.calibrate_btn.add_event_cb(
            lambda e: calibrate_touch(),
            lv.EVENT.CLICKED,
            None,  # ty:ignore[invalid-argument-type]
        )

    def __del__(self):
        if self.screen:
            self.screen.delete()

    def show(self):
        if self.screen:
            lv.screen_load(self.screen)

    def standby(self):
        pass

    def resume(self):
        pass
