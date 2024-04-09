from click import Option as ClickOption


class CloudtokenOption(ClickOption):
    def __init__(self, *args, **kwargs):
        self.plugin_name = None
        if "plugin_name" in kwargs:
            self.plugin_name = kwargs["plugin_name"]
            del kwargs["plugin_name"]

        super().__init__(*args, **kwargs)
