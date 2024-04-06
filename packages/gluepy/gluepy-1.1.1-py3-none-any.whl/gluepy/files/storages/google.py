import os
import logging
from pathlib import Path
from typing import Union
from io import StringIO, BytesIO
from google.cloud import storage
from google.api_core.exceptions import NotFound as GoogleNotFound
from gluepy.conf import default_settings
from .base import BaseStorage

logger = logging.getLogger(__name__)


class GoogleStorage(BaseStorage):
    """ "
    Storage support for Google Cloud Storage.
    """

    separator = "/"

    def __init__(self) -> None:
        super().__init__()
        self.client = storage.Client()
        self.bucket_name = getattr(default_settings, "GOOGLE_GCS_BUCKET", None)
        assert self.bucket_name, "GOOGLE_GCS_BUCKET setting must be set."
        self.bucket = self.client.bucket(self.bucket_name)
        self.storage_root = default_settings.STORAGE_ROOT.lstrip(self.separator)

    def touch(self, file_path: str, content: Union[StringIO, BytesIO]) -> None:
        """Create a new blob at file path.

        Args:
            file_path (str): Path to file we want to create
            content (Union[StringIO, BytesIO]): Content of file we want to generate

        Raises:
            NotImplementedError: Base class raise NotImplementedError
        """
        assert not file_path.endswith(
            self.separator
        ), f"File name cannot end with '{self.separator}'."
        content.seek(0)
        if isinstance(content, StringIO):
            content = BytesIO(content.read().encode("utf-8"))
        self.bucket.blob(self.abspath(file_path)).upload_from_file(content)

    def open(self, file_path: str, mode: str = "rb") -> Union[str, bytes]:
        """Opens a blob at file_path

        Args:
            file_path (str): File path of blob we want to open

        Raises:
            NotImplementedError: Base class raise NotImplementedError
        """
        if mode != "rb":
            logger.warning(f"`mode` is not used for {self.__class__.__name__}")

        stream = BytesIO()
        try:
            self.bucket.blob(self.abspath(file_path)).download_to_file(stream)
        except GoogleNotFound as exc:
            raise FileNotFoundError(
                f"File '{self.abspath(file_path)}' does not exist."
            ) from exc
        stream.seek(0)
        return stream.read()

    def rm(self, path: str, recursive: bool = False) -> None:
        """Delete a file

        Args:
            path (str): Path to file to delete
            recursive (bool): If allowed to delete recursive directories or not.

        Raises:
            NotImplementedError: Base class raise NotImplementedError
        """
        if self.isdir(path):
            files, dirs = self.ls(path)
            if (files or dirs) and not recursive:
                raise FileExistsError(
                    "Option `recursive` must be set to delete directories that "
                    "contain other directories or files."
                )
            for item in files + dirs:
                self.rm(item, recursive=recursive)
        else:
            self.bucket.blob(self.abspath(path=path)).delete()

    def cp(
        self,
        src_path: str,
        dest_path: str,
        recursive: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Copy a file from source to destination

        Args:
            src_path (str): Path to file or directory to copy.
            dest_path (str): Path to file or directory to copy to.
            recursive (bool): If should copy sub directories as well.
            overwrite (bool): If should copy to destination that already exists.
        """
        if not self.exists(src_path):
            raise FileNotFoundError(f"File at '{src_path}' not found.")
        if not self.exists(dest_path) and not overwrite:
            raise FileNotFoundError(f"File at '{dest_path}' not found.")

        if self.isfile(src_path):
            self.touch(dest_path, self.open(src_path))
        elif self.isdir():
            files, dirs = self.ls(src_path)
            if dirs and not recursive:
                raise FileExistsError(
                    "Option `recursive` must be set to copy directories that "
                    "contain other directories."
                )
            paths = files + dirs
            for path in paths:
                self.cp(
                    path,
                    str(
                        Path(dest_path.lstrip(self.separator))
                        / str(Path(path))
                        .relative_to(src_path.lstrip(self.separator))
                        .lstrip(self.separator)
                    ),
                    recursive=recursive,
                    overwrite=overwrite,
                )
        else:
            raise ValueError(
                f"Cannot identify if path '{src_path}' is a file or directory."
            )

    def ls(self, path: str) -> tuple[list[str], list[str]]:
        """List all files and directories at given path.

        Args:
            path (str): Path where we want to list contents of

        Raises:
            NotImplementedError: Base class raise NotImplementedError

        Returns:
            Tuple[List[str], List[str]]:
              First list is files, second list is directories.
        """
        files: list[str] = []
        dirs: list[str] = []

        for blob in self.client.list_blobs(self.bucket, prefix=self.abspath(path)):
            if self.isdir(blob.name):
                dirs += (
                    [
                        f"{self.relpath(blob.name).rstrip(self.separator)}{self.separator}"  # noqa
                    ]
                    if self._is_in_root(blob.name, path)
                    else []
                )
            else:
                if self._is_in_root(os.path.dirname(blob.name), path) and (
                    os.path.dirname(blob.name) != os.path.dirname(self.abspath(path))
                ):
                    dirs += [
                        f"{self.relpath(os.path.dirname(blob.name)).rstrip(self.separator)}{self.separator}"  # noqa
                    ]
                files += (
                    [self.relpath(blob.name)]
                    if self._is_in_root(blob.name, path)
                    else []
                )

        return (
            files,
            dirs,
        )

    def mkdir(self, path: str, make_parents: bool = False) -> None:
        """Make a new directory at location

        Args:
            path (str): Path of directory we want to create
            make_parents (bool, optional): If we should generate parents
              folders as well. Defaults to False.

        Raises:
            NotImplementedError: Base class raise NotImplementedError
        """
        path = path.rstrip(self.separator) + self.separator
        if self.exists(path):
            logger.warning("Directory '%s' already exists.", path)
            return

        parent = os.path.dirname(path)
        if not self.exists(parent) and not make_parents:
            raise FileNotFoundError(
                f"Parent directory '{parent}' does not exist. "
                "Use option `make_parents` to automatically create parent directories."
            )

        self.bucket.blob(self.abspath(path)).upload_from_file(BytesIO())

    def isdir(self, path: str) -> bool:
        """Check if path is directory or not.

        Args:
            path (str): Path we want to check

        Raises:
            NotImplementedError: Base class raise NotImplementedError

        Returns:
            bool: True/False if path is directory or not
        """
        # Ensure always ending with `/`.
        path = self.abspath(path).rstrip(self.separator) + self.separator
        return self.bucket.blob(path).exists() or bool(
            list(self.client.list_blobs(self.bucket, prefix=path, max_results=1))
        )

    def isfile(self, path: str) -> bool:
        """Check if path is a file or not.

        Args:
            path (str): Path we want to check

        Raises:
            NotImplementedError: Base class raise NotImplementedError

        Returns:
            bool: True/False if path is file or not.
        """
        return self.bucket.blob(self.abspath(path=path)).exists() and not path.endswith(
            self.separator
        )

    def exists(self, path: str) -> bool:
        """Check if path exists or not.

        Args:
            path (str): Path we want to check

        Raises:
            NotImplementedError: Base class raise NotImplementedError

        Returns:
            bool: True/False if path is file or not.
        """
        return self.isfile(path) or self.isdir(path)

    def _is_in_root(self, blob_name: str, dir_path: str) -> bool:
        return os.path.dirname(blob_name.strip(self.separator)) == self.abspath(
            dir_path
        ).strip(self.separator)
