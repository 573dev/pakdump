import argparse
from pathlib import Path
from typing import Any, Optional, Sequence, Union


class FullDirPath(argparse.Action):
    """
    argparse.Action subclass to resolve a path and make sure it's a directory
    """

    def __call__(
        self,
        parse: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[str] = None,
    ) -> None:
        """
        Resolve the input path and make sure it doesn't exist (so we can make it
        later), or that it's a directory.
        """
        full_path = Path(str(values)).resolve()
        if full_path.exists() and not full_path.is_dir():
            raise argparse.ArgumentTypeError(f"{self.dest} must be a directory")
        setattr(namespace, self.dest, full_path)


class FullPath(argparse.Action):
    """
    argparse.Action subclass to resolve a path
    """

    def __call__(
        self,
        parse: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, Sequence[Any], None],
        option_string: Optional[str] = None,
    ) -> None:
        """
        Resolve the input path
        """
        full_path = Path(str(values)).resolve()
        setattr(namespace, self.dest, full_path)
