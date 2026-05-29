class AppMeta:
    name: str
    version: str
    directory: str
    entry_point: str
    class_name: str
    hidden: bool

    def __init__(
        self,
        name: str,
        version: str,
        directory: str,
        entry_point: str,
        class_name: str,
        hidden: bool,
    ):
        self.name = name
        self.version = version
        self.directory = directory
        self.entry_point = entry_point
        self.class_name = class_name
        self.hidden = hidden


class BasicApp:
    def show(self):
        pass

    def standby(self):
        pass

    def resume(self):
        pass
