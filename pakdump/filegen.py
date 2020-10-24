import logging
from pathlib import Path

from .dumper import PakDumper


logger = logging.getLogger(__name__)

DEFAULT_FILELIST_PATH = Path(__file__).parent / "filelist.txt"


def test_filename(dumper: PakDumper, filename: Path) -> bool:
    """
    Check if the given filename exists in the pack data
    """
    return dumper.file_exists(filename)


def load_filelist(dumper: PakDumper, filepath: Path = DEFAULT_FILELIST_PATH) -> None:
    """
    Load in the list of files to extract
    """
    with filepath.open() as f:
        for line in f:
            fp = Path(line.strip())
            dumper.file_exists(fp)
