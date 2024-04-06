import yaml
import logging
from io import StringIO
from gluepy.conf import default_context
from gluepy.files.storages import default_storage

logger = logging.getLogger(__name__)

REGISTRY = {}


class Task:
    label = None

    def __init__(self) -> None:
        self.label == self.label or self.__class__.__name__.lower()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        REGISTRY[cls.label] = cls

    def run(self):
        raise NotImplementedError()


class BootstrapTask(Task):
    """Used by default as the START_TASK and injected in each DAG.

    Provide various bootstrapping functionality such as serializing context
    at start of execution.

    """

    label = "bootstraptask"

    def run(self):
        logger.debug(
            f"""
            Run ID: {default_context.gluepy.run_id}
            Run Folder: {default_context.gluepy.run_folder}
            """
        )
        default_storage.touch(
            default_storage.runpath("context.yaml"),
            StringIO(yaml.dump(default_context.to_dict())),
        )
