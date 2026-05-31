import uasyncio as asyncio

import lvgl as lv

from core.hw import connect_wifi, sync_time
from core.ui import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, VIEWPORT_OFFX, VIEWPORT_OFFY
from core.app import BasicApp

import lib.xtime


class SyncClockApp(BasicApp):
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

        self.curr_lbl = lv.label(stack)
        self.curr_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.curr_lbl.set_width(lv.pct(90))
        self.curr_lbl.set_text(
            "Current time: " + lib.xtime.datetime_to_string(lib.xtime.localtimez())
        )

        self.sync_lbl = lv.label(stack)
        self.sync_lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.sync_lbl.set_width(lv.pct(90))
        self.sync_lbl.set_text("New time: -")

        self.sync_btn = lv.button(stack)
        self.sync_btn_txt = lv.label(self.sync_btn)
        self.sync_btn_txt.set_text("Sync clock")

        async def sync_clock(e):
            self.sync_btn.add_state(lv.STATE.DISABLED)
            self.sync_btn_txt.set_text("Connecting...")
            if not await connect_wifi():
                self.sync_btn_txt.set_text("Not connected")
                self.sync_btn.remove_state(lv.STATE.DISABLED)
                return
            self.sync_btn_txt.set_text("Synchronizing...")
            if not await sync_time():
                self.sync_btn_txt.set_text("Failed")
                self.sync_btn.remove_state(lv.STATE.DISABLED)
                return
            self.sync_btn_txt.set_text("Synchronized!")
            self.sync_lbl.set_text(
                "New time: " + lib.xtime.datetime_to_string(lib.xtime.localtimez())
            )
            self.sync_btn.remove_state(lv.STATE.DISABLED)

        self.sync_btn.add_event_cb(
            lambda e: asyncio.create_task(sync_clock(e)),
            lv.EVENT.CLICKED,
            None,  # ty:ignore[invalid-argument-type]
        )

        lv.timer_create(
            lambda tobj: self.curr_lbl.set_text(
                "Current time: " + lib.xtime.datetime_to_string(lib.xtime.localtimez())
            ),
            1000,
            None,
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
