import argparse
import logging
from pathlib import Path
from typing import Optional, Sequence

from pakdump.dumper import PakDumper
from pakdump.filegen import DEFAULT_FILELIST_PATH, load_filelist
from pakdump.utils.ap import FullDirPath, FullPath


logger = logging.getLogger(__name__)
"""pakdump.pakdump_base log object"""


def main(args: Optional[Sequence[str]] = None) -> None:
    """
    Dump data from GFDM V8 '.pak' files

    Args:
        args (Optional[Sequence[str]]) = None: Arguments List
    """

    p_args = parse_args(args)
    logging.basicConfig(
        level=p_args.log_level,
        format="[ %(asctime)s | %(levelname)-8s | %(name)s ] %(message)s",
    )

    # Create a dumper object, and dump the data
    dumper = PakDumper(p_args.input, p_args.output, p_args.force)

    if p_args.test_filepath != []:
        for filepath in p_args.test_filepath:
            exists = dumper.file_exists(filepath)

            if exists:
                print(f"Filepath exists: {filepath}")
            else:
                print(f"Filepath does not exist: {filepath}")
    elif p_args.extract_filepath != []:
        for filepath in p_args.extract_filepath:
            _ = dumper.file_exists(filepath)

        dumper.dump()
    else:
        # Gen all the files and dump
        load_filelist(dumper, filepath=p_args.filelist_path)

        # Dump only if this isn't a dry run
        if not p_args.dryrun:
            dumper.dump()
        else:
            found = len(
                [1 for k in dumper.entries if dumper.entries[k].filename is not None]
            )
            print(f"Total files: {len(dumper.entries)}")
            print(f"Files found: {found}")
            print(f"    Missing: {len(dumper.entries) - found}")


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """
    Parse the arguments

    Args:
        args (Optional[Sequence[str]]) = None: Arguments List

    Returns:
        :class:`argparse.Namespace`: Namespace object of all parsed arguments

    Raises:
        :class:`argparse.ArgumentTypeError`: If input path doesn't point to the `data`
            dir
    """

    parser = argparse.ArgumentParser(
        description="Dump data from GFDM V8 '.pak' files",
    )
    parser.add_argument(
        "-i",
        "--input",
        action=FullDirPath,
        type=Path,
        required=True,
        help="Path to GFDM Data directory",
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
        "-t",
        "--test-filepath",
        type=Path,
        default=[],
        nargs="+",
        help="Test one or more file paths to see if they exist in the pack data",
    )
    parser.add_argument(
        "-e",
        "--extract-filepath",
        type=Path,
        default=[],
        nargs="+",
        help="Extract one or more file paths if they exist",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="write out all extracted files even if they already exist",
    )
    parser.add_argument(
        "-p",
        "--filelist-path",
        action=FullPath,
        type=Path,
        default=DEFAULT_FILELIST_PATH,
        help="Path to list of files to extract",
    )
    parser.add_argument(
        "-r",
        "--dryrun",
        action="store_true",
        help="Perform a dry run. Don't actually extract any files",
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

    if parsed_args.input.parts[-1] != "data":
        raise argparse.ArgumentTypeError("input must be in the GFDM `data` directory")

    return parsed_args


if __name__ == "__main__":
    main()
