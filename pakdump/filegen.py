import logging
from pathlib import Path
from typing import List

from .dumper import PakDumper


logger = logging.getLogger(__name__)


def bruteforce_filenames(dumper: PakDumper) -> List[Path]:
    """
    Generate a list of all possible filenames for output files

    The file data is stored in packinfo.bin using crc32 and crc16 checksums, thus you
    can't actually export the file from the packs unless you know its name.
    """
    # TODO: Potentialy we don't even need to store this list as checking if the file
    # exists in the dumper, sets that filename for the hash
    filenames: List[Path] = []

    def add_filenames(basedir: str, files: List[str]) -> None:
        new_files = [basedir + f for f in files]

        for f in new_files:
            filepath = Path(f)
            if dumper.file_exists(filepath):
                filenames.append(filepath)

    """
    # known filenames in: /data/product/music
    basedir = "/data/product/music/"
    files = [
        "course_info.bin",
        "jp_title.bin",
        "mdb.bin",
        "mdb.xml",
        "mdbe.bin",
        "mdbe.xml",
        "music_info.bin",
        "net_id.bin",
    ]
    add_filenames(basedir, files)

    # known filenames in: /data/product/music/system
    basedir = "/data/product/music/system/"
    files = [
        "dmv8_dflt.va3",
        "dmv8_se.va3",
        "ealogo_gf.pss",
        "gfc_se.va3",
        "gfv8_dflt.va3",
        "gfv8_se.va3",
        "gfv_se.va2",
        "se.va2",
    ]

    # generated va2 and va3 files in: /data/product/music/system
    ftypes = ["va2", "va3"]
    for i in range(0, 500):
        for j in range(0, 500):
            for ftype in ftypes:
                files.extend(
                    [
                        f"dmv{i}_v{j:02}.{ftype}",
                        f"dm{i}_v{j:02}.{ftype}",
                        f"gfv{i}_v{j:02}.{ftype}",
                        f"gf{i}_v{j:02}.{ftype}",
                    ]
                )
        for ftype in ftypes:
            files.extend(
                [
                    f"dm_v{i:02}.{ftype}",
                    f"dmv_v{i:02}.{ftype}",
                    f"dmv{i}_se.{ftype}",
                    f"dm{i}_se.{ftype}",
                    f"gf_v{i:02}.{ftype}",
                    f"gfv_v{i:02}.{ftype}",
                    f"gfv{i}_se.{ftype}",
                    f"gf{i}_se.{ftype}",
                ]
            )

    # generated m2v files in: /data/product/music/system
    for i in range(0, 500):
        files.append(f"system{i:02}.m2v")

    # Generated bin, va2, va3, and pss files in: /data/product/music/system
    # Using system audio part names
    system_audio_parts = [
        "V6CM01",
        "V6CM02",
        "V6CM03",
        "b_info",
        "b_result",
        "battle",
        "battle01",
        "battle02",
        "battle_result",
        "clear",
        "entry",
        "information",
        "jukebox",
        "konami",
        "p_custom",
        "phase",
        "phase_check",
        "playdata",
        "q_result",
        "q_select",
        "ranking",
        "result",
        "result_total",
        "scale",
        "scale_check",
        "select",
        "session",
        "title",
        "v8_entry",
        "v8_logo",
        "v8_result",
        "v8_thankyou",
        "volume",
        "volume_check",
    ]

    for audio_part in system_audio_parts:
        for ftype in ["bin", "va2", "va3", "pss"]:
            for game in ["_gf", "_dm", ""]:
                files.append(f"{audio_part}{game}.{ftype}")
    add_filenames(basedir, files)
    """
    add_filenames("/data/pkg/", ["filelist.xml"])
    add_filenames(
        "/pj/gfv2/data/product",
        [
            "info",
            "psize",
            "alias",
            "item",
            "name",
            "offset",
            "fsize",
            "time",
            "uri",
            "pss",
        ],
    )

    # TODO: This list should be generated outside of this program and read in as it
    # takes a long time to generate it
    return filenames
