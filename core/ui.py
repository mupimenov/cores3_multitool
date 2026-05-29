import time
from micropython import const

import lvgl as lv

import task_handler

from core.hw import DISPLAY_WIDTH, get_pmic
from core.app_manager import AppManager

import lib.xtime

STATUSBAR_HEIGHT = const(30)
VIEWPORT_WIDTH = const(320)
VIEWPORT_HEIGHT = const(207)
VIEWPORT_OFFX = const(0)
VIEWPORT_OFFY = const(33)

app_manager = None
home = None
status_bar = None


class Home:
    def __init__(self, app_manger: AppManager):
        self.app_manager = app_manger
        self.screen = lv.screen_active()
        self.screen.set_style_bg_color(lv.color_hex(0x000000), lv.PART.MAIN)

        lst = lv.list(self.screen)
        lst.set_size(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        lst.set_pos(VIEWPORT_OFFX, VIEWPORT_OFFY)
        menu = lst.add_text("Menu")
        menu.set_height(30)
        menu.align(lv.ALIGN.CENTER, 0, 0)

        for meta in app_manger.metas:
            if meta.hidden:
                continue
            btn = lst.add_button(lv.SYMBOL.DUMMY, meta.name)
            btn.set_height(40)
            btn.add_event_cb(
                lambda e, m=meta: app_manger.open_app(m),
                lv.EVENT.CLICKED,
                None,  # ty:ignore[invalid-argument-type]
            )

        shtd_btn = lst.add_button(lv.SYMBOL.POWER, "Shutdown")
        shtd_btn.set_height(40)

        def shutdown(mbox):
            pmic = get_pmic()
            if pmic:
                pmic.shutdown()
            mbox.close()

        def on_shutdown_clicked(e):
            mbox = lv.msgbox(self.screen)
            mbox.add_title("Shutting down")
            mbox.add_text("Are you sure?")
            btn_yes = mbox.add_footer_button("Yes")
            btn_no = mbox.add_footer_button("No")
            btn_yes.add_event_cb(lambda e: shutdown(mbox), lv.EVENT.CLICKED, None)  # ty:ignore[invalid-argument-type]
            btn_no.add_event_cb(
                lambda e: mbox.close(),
                lv.EVENT.CLICKED,
                None,  # ty:ignore[invalid-argument-type]
            )
            mbox.center()

        shtd_btn.add_event_cb(on_shutdown_clicked, lv.EVENT.CLICKED, None)  # ty:ignore[invalid-argument-type]

    def show(self):
        lv.screen_load(self.screen)


class StatusBar:
    def __init__(self, app_manager: AppManager, home: Home):
        sys_layer = lv.layer_sys()

        self.status_bar = lv.obj(sys_layer)
        self.status_bar.set_size(DISPLAY_WIDTH, STATUSBAR_HEIGHT)
        self.status_bar.set_style_bg_color(lv.color_hex(0x333333), 0)
        self.status_bar.set_style_border_width(0, 0)
        self.status_bar.set_style_pad_all(0, 0)

        self.home_btn = lv.button(self.status_bar)
        self.home_btn.align(lv.ALIGN.LEFT_MID, 5, 0)
        self.home_btn.set_height(STATUSBAR_HEIGHT - 6)
        self.home_btn.set_style_pad_top(5, 0)

        def show_home(e):
            current_app = app_manager.current_app()
            if current_app:
                home.show()
                _ = app_manager.close_app(current_app)

        self.home_btn.add_event_cb(show_home, lv.EVENT.CLICKED, None)  # ty:ignore[invalid-argument-type]

        self.home_label = lv.label(self.home_btn)
        self.home_label.set_text("Home")
        self.home_label.set_style_text_color(lv.color_white(), 0)

        self.time_label = lv.label(self.status_bar)
        self.time_label.align(lv.ALIGN.LEFT_MID, 258, 0)
        self.time_label.set_text("00:00:00")

        lv.timer_create(
            lambda tobj: self._update_time(),
            250,
            None,
        )

    def _update_time(self):
        s = lib.xtime.datetime_to_time_string(lib.xtime.localtimez())
        self.time_label.set_text(s)


def init():
    global app_manager
    global status_bar
    global home

    app_manager = AppManager()
    app_manager.scan_apps()

    home = Home(app_manager)
    status_bar = StatusBar(app_manager, home)

    th = task_handler.TaskHandler()

    while True:
        time.sleep(0.033)
