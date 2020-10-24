import argparse
import logging
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from .dumper import PakDumper
from .filegen import DEFAULT_FILELIST_PATH, load_filelist, test_filename


logger = logging.getLogger(__name__)


def main(args: Optional[Sequence[str]] = None) -> None:
    p_args = parse_args(args)
    logging.basicConfig(
        level=p_args.log_level,
        format="[ %(asctime)s | %(levelname)-8s | %(name)s ]\n%(message)s",
    )

    # Create a dumper object, and dump the data
    dumper = PakDumper(p_args.input, p_args.output, p_args.force)

    if p_args.test_filepath != []:
        for filepath in p_args.test_filepath:
            # Test a file, print the result and exit
            exists = test_filename(dumper, filepath)

            if exists:
                print(f"Filepath exists: {filepath}")
            else:
                print(f"Filepath does not exist: {filepath}")
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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Dump data from GFDM v8 '.pak' files",
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
        help="Test a single file path to see if it exists in the pack data",
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
        action=FullDirPath,
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
        description="Control what log level the log outputs (default: logger.ERROR)",
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


class FullDirPath(argparse.Action):
    """
    Expand path to abspath and make sure it's a directory
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


if __name__ == "__main__":
    main()
