import logging.config
from gluepy.conf import default_settings
from gluepy.utils.loading import import_module


def bootstrap():
    if not hasattr(default_settings, "INSTALLED_MODULES"):
        return

    logging.config.dictConfig(default_settings.LOGGING)
    for module in default_settings.INSTALLED_MODULES:
        import_module(".".join([module, "tasks"]))
        import_module(".".join([module, "dags"]))
