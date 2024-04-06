import os
from gluepy.utils.loading import LazyProxy, import_module, SingletonMixin


class Settings(SingletonMixin):
    def __init__(self, dotted_path: str, *args, **kwargs):
        module = import_module(dotted_path)
        for key in dir(module):
            if key.isupper():
                setattr(self, key, getattr(module, key))


default_settings = LazyProxy(lambda: Settings(os.environ.get("GLUEPY_SETTINGS_MODULE")))
