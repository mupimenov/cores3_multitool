import os
import json

from core.app import AppMeta, BasicApp


class AppManager:
    def __init__(self):
        self.metas: list[AppMeta] = []
        self.apps: list[BasicApp] = []

    def scan_apps(self):
        self.metas.clear()
        app_dir = "app"
        for entry in os.ilistdir(f"/{app_dir}"):
            name = entry[0]
            entry_type = entry[1]
            if entry_type == 0x4000:
                manifest_path = f"/{app_dir}/{name}/manifest.json"
                try:
                    mode = os.stat(manifest_path)[0]
                except Exception:
                    continue
                if mode & 0x8000:
                    with open(manifest_path, "r") as f:
                        try:
                            meta = json.load(f)
                            self.metas.append(
                                AppMeta(
                                    meta["name"],
                                    meta["version"],
                                    f"{app_dir}/{name}",
                                    meta["entry_point"],
                                    meta["class_name"],
                                    meta["hidden"] if "hidden" in meta else False,
                                )
                            )
                        except Exception:
                            continue

    def push_app(self, app: BasicApp):
        self.apps.append(app)

    def current_app(self) -> BasicApp | None:
        if len(self.apps) == 0:
            return None
        return self.apps[-1]

    def pop_app(self) -> BasicApp:
        return self.apps.pop()

    def open_app(self, meta: AppMeta) -> bool:
        if not meta:
            return False
        try:
            current_app = self.current_app()
            if current_app:
                current_app.standby()
            mod_name = meta.directory + "/" + meta.entry_point.replace(".py", "")
            mod_name = mod_name.replace("/", ".")
            app_mod = __import__(mod_name)
            for submodule in mod_name.split(".")[1:]:
                app_mod = getattr(app_mod, submodule)
            app_cls = getattr(app_mod, meta.class_name)
            app: BasicApp = app_cls()
            self.push_app(app)
            app.show()
            return True
        except Exception as ex:
            print(f'Failed to open app "{meta.name}": {ex}')
        return False

    def close_app(self, app: BasicApp) -> BasicApp | None:
        self.apps.remove(app)
        del app
        if len(self.apps):
            next_app = self.current_app()
            if next_app:
                next_app.resume()
            return next_app
        return None
