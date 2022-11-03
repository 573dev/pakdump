import argparse
import logging
from pathlib import Path
from typing import Optional, Sequence

from pakdump.mdbe import MDB
from pakdump.utils.ap import FullPath


logger = logging.getLogger(__name__)
"""pakdump.mdbcreate_base log object"""


def main(args: Optional[Sequence[str]] = None) -> None:
    """
    Read in JSON encoded MDB data, Encrypt and dump into binary `mdbe.bin` format  for
    GFDM V8

    Args:
        args (Optional[Sequence[str]]) = None: Arguments List
    """

    p_args = parse_args(args)
    logging.basicConfig(
        level=p_args.log_level,
        format="[ %(asctime)s | %(levelname)-8s | %(name)s ]\n%(message)s",
    )

    MDB(p_args.input, p_args.output, p_args.force)


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """
    Parse the arguments

    Args:
        args (Optional[Sequence[str]]) = None: Arguments List

    Returns:
        :class:`argparse.Namespace`: Namespace object of all parsed arguments

    Raises:
        :class:`argparse.ArgumentTypeError`: If input path doesn't point to `mdbe.bin`
    """

    parser = argparse.ArgumentParser(
        description=(
            "Read in JSON encoded MusidDB data, encrypt it and dump it into the binary "
            "`mdbe.bin` format for GFDM V8"
        )
    )
    parser.add_argument(
        "-i",
        "--input",
        action=FullPath,
        type=Path,
        required=True,
        help="Path to JSON formated MusicDB file",
    )
    parser.add_argument(
        "-o",
        "--output",
        action=FullPath,
        type=Path,
        required=True,
        help="Path to output `mdbe.bin` file.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite the output file even if it already exists",
    )

    logger_group_parent = parser.add_argument_group(
        title="logging arguments",
        description="Control what log level the log outputs (default: ERROR)",
    )
    logger_group = logger_group_parent.add_mutually_exclusive_group()
    default_log_level = logging.ERROR

    logger_group.add_argument(
        "-d",
        "--debug",
        dest="log_level",
        action="store_const",
        const=logging.DEBUG,
        default=default_log_level,
        help="Set log level to DEBUG",
    )
    logger_group.add_argument(
        "-v",
        "--verbose",
        dest="log_level",
        action="store_const",
        const=logging.INFO,
        default=default_log_level,
        help="Set log level to INFO",
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.input.suffix.lower() != ".json":
        raise argparse.ArgumentTypeError('input must be a ".json" file')

    return parsed_args


if __name__ == "__main__":
    main()
