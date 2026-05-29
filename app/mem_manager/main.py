import gc

import lvgl as lv

from core.ui import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, VIEWPORT_OFFX, VIEWPORT_OFFY
from core.app import BasicApp


class MemManagerApp(BasicApp):
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

        self.alloc_lbl = lv.label(stack)
        self.alloc_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.alloc_lbl.set_width(lv.pct(90))

        self.free_lbl = lv.label(stack)
        self.free_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.free_lbl.set_width(lv.pct(90))

        self.collect_btn = lv.button(stack)
        self.collect_btn_txt = lv.label(self.collect_btn)
        self.collect_btn_txt.set_text("Collect")

        def collect_mem(e):
            gc.collect()
            self._show_mem()

        self.collect_btn.add_event_cb(collect_mem, lv.EVENT.CLICKED, None)  # ty:ignore[invalid-argument-type]

        self._show_mem()

    def __del__(self):
        if self.screen:
            self.screen.delete()

    def _show_mem(self):
        self.alloc_lbl.set_text(
            f"Allocated: {gc.mem_alloc() / 1024: .1f} KB"  # ty:ignore[unresolved-attribute]
        )
        self.free_lbl.set_text(f"Free: {gc.mem_free() / 1024: .1f} KB")  # ty:ignore[unresolved-attribute]

    def show(self):
        if self.screen:
            lv.screen_load(self.screen)

    def standby(self):
        pass

    def resume(self):
        pass
