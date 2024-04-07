from pathlib import Path
from typing import Any, Optional, Sequence, Tuple, Union

import watchfiles

from faststream.cli.supervisors.basereload import BaseReload
from faststream.log import logger
from faststream.types import DecoratedCallable


class ExtendedFilter(watchfiles.PythonFilter):  # type: ignore[misc]
    """A class that extends the `watchfiles.PythonFilter` class."""

    def __init__(
        self,
        *,
        ignore_paths: Optional[Sequence[Union[str, Path]]] = None,
        extra_extensions: Sequence[str] = (),
    ) -> None:
        """Initialize the class.

        Args:
            ignore_paths: Optional sequence of paths to ignore.
            extra_extensions: Sequence of extra extensions to include.

        Returns:
            None

        """
        super().__init__(ignore_paths=ignore_paths, extra_extensions=extra_extensions)
        self.ignore_dirs: Sequence[str] = (
            *self.ignore_dirs,
            "venv",
            "env",
            ".github",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
        )


class WatchReloader(BaseReload):
    """A class to reload a target function when files in specified directories change."""

    def __init__(
        self,
        target: DecoratedCallable,
        args: Tuple[Any, ...],
        reload_dirs: Sequence[Union[Path, str]],
        reload_delay: float = 0.3,
        extra_extensions: Sequence[str] = (),
    ) -> None:
        """Initialize a WatchFilesReloader object.

        Args:
            target : the function to be reloaded
            args : arguments to be passed to the target function
            reload_dirs : directories to watch for file changes
            reload_delay : delay in seconds between each check for file changes
            extra_extensions: A sequence of extra extensions to include.

        Returns:
            None.

        """
        super().__init__(target, args, reload_delay)
        self.reloader_name = "WatchFiles"
        self.reload_dirs = reload_dirs
        self.watcher = watchfiles.watch(
            *reload_dirs,
            step=int(reload_delay * 1000),
            watch_filter=ExtendedFilter(extra_extensions=extra_extensions),
            stop_event=self.should_exit,
            yield_on_timeout=True,
        )

    def startup(self) -> None:
        logger.info(f"Will watch for changes in these directories: {self.reload_dirs}")
        super().startup()

    def should_restart(self) -> bool:
        for changes in self.watcher:  # pragma: no branch
            if changes:  # pragma: no branch
                unique_paths = {Path(c[1]).name for c in changes}
                message = "WatchReloader detected file change in '%s'. Reloading..."
                logger.info(message % tuple(unique_paths))
                return True
        return False  # pragma: no cover
