# flake8: noqa
from gluepy.conf import default_settings
from gluepy.utils.loading import LazyProxy, import_string, SingletonMixin
from .local import LocalStorage
from .s3 import S3Storage
from .google import GoogleStorage


default_storage = LazyProxy(lambda: import_string(default_settings.STORAGE_BACKEND)())
