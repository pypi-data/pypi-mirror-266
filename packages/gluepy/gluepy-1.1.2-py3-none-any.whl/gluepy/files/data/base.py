from typing import Any


class BaseDataManager:
    """Base abstract class for data managers
    that define interface.
    """

    def read(self, path: str, root: bool = False, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def read_sql(self, sql: str, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def write(self, path: str, df: Any, root: bool = False, *args, **kwargs) -> None:
        raise NotImplementedError()
