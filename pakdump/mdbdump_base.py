import argparse
import logging
from pathlib import Path
from typing import Optional, Sequence

from pakdump.mdbe import MDB
from pakdump.utils.ap import FullDirPath, FullPath


logger = logging.getLogger(__name__)
"""pakdump.mdbdump_base log object"""


def main(args: Optional[Sequence[str]] = None) -> None:
    """
    Decrypt and dump the musicdb from the `mdbe.bin` file from GFDM V8

    Args:
        args (Optional[Sequence[str]]) = None: Arguments List
    """

    p_args = parse_args(args)
    logging.basicConfig(
        level=p_args.log_level,
        format="[ %(asctime)s | %(levelname)-8s | %(name)s ]\n%(message)s",
    )

    mdb = MDB(
        p_args.input, p_args.output, p_args.force, pretty_print=p_args.pretty_print
    )
    mdb.export(p_args.format)


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
            "Decrypt and dump the musicdb from the `mdbe.bin` file from GFDM V8 as JSON"
        )
    )
    parser.add_argument(
        "-i",
        "--input",
        action=FullPath,
        type=Path,
        required=True,
        help="Path to mdbe.bin file",
    )
    parser.add_argument(
        "-o",
        "--output",
        action=FullDirPath,
        type=Path,
        default=Path.cwd(),
        help="Path to output directory. Defaults to your current working directory",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite the drcrypted data even if it already exists",
    )
    parser.add_argument(
        "-t",
        "--format",
        type=str,
        choices=["JSON", "XML"],
        default="JSON",
        help="output format",
    )

    parser.add_argument(
        "-p",
        "--pretty-print",
        action="store_true",
        help="enable pretty print for the output file",
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

    if not parsed_args.input.parts[-1].endswith("mdbe.bin"):
        raise argparse.ArgumentTypeError('input must be the "mdbe.bin" file')

    return parsed_args


if __name__ == "__main__":
    main()
