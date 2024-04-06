from typing import List

from gluepy.exec.tasks import Task
from gluepy.utils.loading import import_string
from gluepy.conf import default_settings


class DAG:
    label = None
    extra_options = {}
    tasks = []

    def __init__(self) -> None:
        self.label == self.label or self.__class__.__name__.lower()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        REGISTRY[cls.label] = cls

    def inject_tasks(self) -> List[Task]:
        """Inject all tasks including START_TASK to the final
        list of executable tasks of this DAG.

        Returns:
            List[Task]: Full list of tasks of DAG.
        """
        return [import_string(default_settings.START_TASK)] + self.tasks


REGISTRY = {}
