import logging
from pathlib import Path

from pakdump.dumper import PakDumper


logger = logging.getLogger(__name__)
"""pakdump.filegen log object"""

DEFAULT_FILELIST_PATH = Path(__file__).parent / "filelist.txt"
"""Location of our default filelist"""


def load_filelist(dumper: PakDumper, filepath: Path = DEFAULT_FILELIST_PATH) -> None:
    """
    Load in the list of files to extract into the PakDumper object

    Args:
        dumper (:class:`pakdump.dumper.PakDumper`): Instantiated PakDumper object
    """
    with filepath.open() as f:
        for line in f:
            fp = Path(line.strip())
            dumper.file_exists(fp)
