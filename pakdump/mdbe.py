from __future__ import annotations

import json
import logging
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lxml import etree
from lxml.builder import E


logger = logging.getLogger(__name__)


def __xe(name: str, body: Any, type: str, count: int = 1) -> E:
    """
    Helper function to build an xml element with `__type` and `__count` attributes if
    necessary.

    Args:
        name (str): XML Element Name
        body (Any): XML Element Body (or text)
        type (str): type of `body` element (i.e. u8, s32, etc)
        count (int) = 1: How many elements of `type` exist in `body`

    Returns:
        XML Element :obj:`E`: Constructed XML Element
    """
    attrs = {"__type": type}
    if count > 1:
        attrs["__count"] = str(count)
    return E(name, str(body), attrs)


class MDBHeader(object):
    """
    GFDM V8 MDB (Music DB) Header object. Contains all the header data extracted from
    `mdbe.bin`.

    Args:
        id (str): Header Game ID
        format (int): Header Format Type
        checksum (int): Header Checksum Value
        header_size (int): Size of header data in bytes
        record_size (int): Size of song record in bytes
        record_number (int): Number of song records contained in the file
        course_size (int): Size of course data in bytes
        course_number (int): Number of courses contained in the file
    """

    STRUCT_FORMAT = "<8biihhhhh"
    """Binary data format. Used in `struct.unpack_from`"""
    DATA_SIZE = 0x40
    """Size of the header data"""

    def __init__(
        self,
        id: str,
        format: int,
        checksum: int,
        header_size: int,
        record_size: int,
        record_number: int,
        course_size: int,
        course_number: int,
    ) -> None:
        self.id = id
        self.format = format
        self.checksum = checksum
        self.header_size = header_size
        self.record_size = record_size
        self.record_number = record_number
        self.course_size = course_size
        self.course_number = course_number

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dict

        Returns:
            Dict[str, Any]: Music DB Header as a dict
        """
        return {
            "id": self.id,
            "format": self.format,
            "checksum": self.checksum,
            "header_size": self.header_size,
            "record_size": self.record_size,
            "record_number": self.record_number,
            "course_size": self.course_size,
            "course_number": self.course_number,
        }

    def to_xml(self) -> etree:
        """
        Convert to an XML tree

        Returns:
            :class:`lxml.etree`: Music DB Header as XML tree
        """
        return E.header(
            E.data(
                __xe(
                    "id", " ".join(map(str, bytearray(self.id, "UTF-8"))), "s8", count=8
                ),
                __xe("format", self.format, "s32"),
                __xe("chksum", self.checksum, "s32"),
                __xe("header_sz", self.header_size, "s16"),
                __xe("record_sz", self.record_size, "s16"),
                __xe("record_nr", self.record_number, "s16"),
                __xe("course_sz", self.course_size, "s16"),
                __xe("course_nr", self.course_number, "s16"),
            )
        )

    def __repr__(self) -> str:
        return (
            f'MDBHeader<id: "{self.id}", format: {self.format}, '
            f"checksum: {self.checksum}, header_size: {self.header_size}, "
            f"record_size: {self.record_size}, record_number: {self.record_number}, "
            f"course_size: {self.course_size}, course_number: {self.course_number}>"
        )

    @classmethod
    def from_byte_data(cls, data: Tuple[Any, ...]) -> MDBHeader:
        """
        Build an :class:`.MDBHeader` object from the raw bytes extracted from `mdbe.bin`

        Args:
            data (Tuple[Any, ...]): Tuple containing the unpacked data

        Returns:
            :class:`.MDBHeader`: Header object
        """
        id = bytes(data[0:8]).decode("UTF-8")
        (
            format,
            checksum,
            header_size,
            record_size,
            record_number,
            course_number,
            course_size,
        ) = data[8:]

        return MDBHeader(
            id,
            format,
            checksum,
            header_size,
            record_size,
            record_number,
            course_size,
            course_number,
        )


class MDBDifficulty(object):
    """
    Holds all the difficulty values for a song for a single instrument.

    Args:
        beginner (int): Beginner Difficulty Value
        basic (int): Basic Difficulty Value
        advanced (int): Advanced Difficulty Value
        extreme (int): Extreme Difficulty Value
    """

    def __init__(self, beginner: int, basic: int, advanced: int, extreme: int) -> None:
        self.beginner = beginner
        self.basic = basic
        self.advanced = advanced
        self.extreme = extreme

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dict

        Returns:
            Dict[str, Any]: Difficulty as a dict
        """
        return {
            "beginner": self.beginner,
            "basic": self.basic,
            "advanced": self.advanced,
            "extreme": self.extreme,
        }

    def str_values(self) -> str:
        """
        Convert to a string

        Returns:
            str: A space delimited string of all 4 difficulty values
        """
        return f"{self.beginner} {self.basic} {self.advanced} {self.extreme}"

    def __repr__(self) -> str:
        return (
            f"MDBDifficulty<beginner: {self.beginner}, basic: {self.basic}, "
            f"advanced: {self.advanced}, extreme: {self.extreme}>"
        )


class MDBDifficultyList(object):
    """
    Holds all the different :class:`.MDBDifficulty` objects for each instrument. Guitar,
    Bass, Open, and Drum.

    Args:
        guitar (:class:`.MDBDifficuly`): Guitar Difficulty
        bass (:class:`.MDBDifficuly`): Bass Difficulty
        open_pick (:class:`.MDBDifficuly`): Open Difficulty
        drum (:class:`.MDBDifficuly`): Drum Difficulty
    """

    def __init__(
        self,
        guitar: MDBDifficulty,
        bass: MDBDifficulty,
        open_pick: MDBDifficulty,
        drum: MDBDifficulty,
    ) -> None:
        self.guitar = guitar
        self.bass = bass
        self.open_pick = open_pick
        self.drum = drum

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dict

        Returns:
            Dict[str, Any]: Difficulty List as a dict
        """
        return {
            "guitar": self.guitar.to_dict(),
            "bass": self.bass.to_dict(),
            "open": self.open_pick.to_dict(),
            "drum": self.drum.to_dict(),
        }

    def to_xml(self) -> etree:
        """
        Convert to an XML tree

        Returns:
            :class:`lxml.etree`: Difficulty List as XML tree
        """
        body = (
            f"{self.guitar.str_values()} {self.bass.str_values()} "
            f"{self.open_pick.str_values()} {self.drum.str_values()}"
        )
        return __xe("classics_diff_list", body, "u8", count=16)

    def __repr__(self) -> str:
        return (
            f"MDBDifficultyList<guitar: {self.guitar}, bass: {self.bass}, "
            f"open_pick: {self.open_pick}, drum: {self.drum}>"
        )


class MDBSong(object):
    """
    Holds all the information for a single GFDM Song

    Args:
        music_id (int): Music ID
        difficulty (:class:`.MDBDifficultyList`): Difficulty values
        pad_diff (int): Unknown
        seq_flag (int): Unknown (sequence flag?)
        contain_stat (Tuple[int, int]): Unknown
        b_long (bool): Song is Long Version
        b_eemall (bool): Song is an EEmall song
        bpm (int): Song BPM
        bpm2 (int): Unknown (maybe highest bpm value in the song)
        title_ascii (str): ASCII version of the song title. Max 16 chars
        order_ascii (int): Unknown (Some sort of ascii ordering index)
        order_kana (int): Unknown (Similar to order ascii but for kana?)
        category_kana (int): Unknown (Some sort of kana category id?)
        secret (Tuple[int, int]): Unknown (Designates a secret song?)
        b_session (bool): Unknown (Maybe designates a session only song?)
        speed (int): Unknown
        life (int): Unknown
        gf_offset (int): Unknown
        dm_offset (int): Unknown
        chart_list (List[int]): Unknown
        origin: (int): Unknown (Version of the game it came out on?)
        music_type (int): Unknown
        genre (int): Unknown (some sort of genre sort?)
        is_remaster (int): Unknown
    """

    STRUCT_FORMAT = "<i16BHH2BBBHH16BHHB2BBBBbb128BBBBB"
    """Binary data format. Used in `struct.unpack_from`"""

    def __init__(
        self,
        music_id: int,
        difficulty: MDBDifficultyList,
        pad_diff: int,
        seq_flag: int,
        contain_stat: Tuple[int, int],
        b_long: bool,
        b_eemall: bool,
        bpm: int,
        bpm2: int,
        title_ascii: str,
        order_ascii: int,
        order_kana: int,
        category_kana: int,
        secret: Tuple[int, int],
        b_session: bool,
        speed: int,
        life: int,
        gf_offset: int,
        dm_offset: int,
        chart_list: List[int],
        origin: int,
        music_type: int,
        genre: int,
        is_remaster: int,
    ):
        self.music_id = music_id
        self.difficulty = difficulty
        self.pad_diff = pad_diff
        self.seq_flag = seq_flag
        self.contain_stat = contain_stat
        self.b_long = b_long
        self.b_eemall = b_eemall
        self.bpm = bpm
        self.bpm2 = bpm2
        self.title_ascii = title_ascii
        self.order_ascii = order_ascii
        self.order_kana = order_kana
        self.category_kana = category_kana
        self.secret = secret
        self.b_session = b_session
        self.speed = speed
        self.life = life
        self.gf_offset = gf_offset
        self.dm_offset = dm_offset
        self.chart_list = chart_list
        self.origin = origin
        self.music_type = music_type
        self.genre = genre
        self.is_remaster = is_remaster

    @classmethod
    def from_byte_data(cls, data: Tuple[Any, ...]) -> MDBSong:
        """
        Build an :class:`.MDBSong` object from the raw bytes extracted from `mdbe.bin`

        Args:
            data (Tuple[Any, ...]): Tuple containing the unpacked data

        Returns:
            :class:`.MDBSong`: Song object
        """
        # First just split up the tuple in to the different sections
        music_id = data[0]
        diff_list = data[1:17]
        pad_diff = data[17]
        seq_flag = data[18]
        contain_stat = data[19:21]
        b_long = data[21]
        b_eemall = data[22]
        bpm = data[23]
        bpm2 = data[24]
        title_ascii = data[25:40]
        order_ascii = data[40]
        order_kana = data[41]
        category_kana = data[42]
        secret = data[43:45]
        b_session = data[45]
        speed = data[46]
        life = data[47]
        gf_offset = data[48]
        dm_offset = data[49]
        chart_list = data[50:179]
        origin = data[179]
        music_type = data[180]
        genre = data[181]
        is_remaster = data[182]

        # Create a proper difficulty object
        difficulty = MDBDifficultyList(
            MDBDifficulty(*diff_list[0:4]),
            MDBDifficulty(*diff_list[4:8]),
            MDBDifficulty(*diff_list[8:12]),
            MDBDifficulty(*diff_list[12:16]),
        )

        return MDBSong(
            music_id,
            difficulty,
            pad_diff,
            seq_flag,
            (contain_stat[0], contain_stat[1]),
            True if b_long == "1" else False,
            True if b_eemall == "1" else False,
            bpm,
            bpm2,
            bytes(title_ascii).decode("UTF-8").strip(),
            order_ascii,
            order_kana,
            category_kana,
            (secret[0], secret[1]),
            True if b_session == "1" else False,
            speed,
            life,
            gf_offset,
            dm_offset,
            list(chart_list),
            origin,
            music_type,
            genre,
            is_remaster,
        )

    def to_dict(self) -> dict:
        """
        Convert to a dict

        Returns:
            Dict[str, Any]: Music DB Song as a dict
        """
        return {
            "music_id": self.music_id,
            "difficulty": self.difficulty.to_dict(),
            "pad_diff": self.pad_diff,
            "seq_flag": self.seq_flag,
            "contain_stat": self.contain_stat,
            "b_long": self.b_long,
            "b_eemall": self.b_eemall,
            "bpm": self.bpm,
            "bpm2": self.bpm2,
            "title_ascii": "".join(i for i in self.title_ascii if 31 < ord(i) < 127),
            "order_ascii": self.order_ascii,
            "order_kana": self.order_kana,
            "category_kana": self.category_kana,
            "secret": self.secret,
            "b_session": self.b_session,
            "speed": self.speed,
            "life": self.life,
            "gf_offset": self.gf_offset,
            "dm_offset": self.dm_offset,
            "chart_list": self.chart_list,
            "origin": self.origin,
            "music_type": self.music_type,
            "genre": self.genre,
            "is_remaster": self.is_remaster,
        }

    def to_xml(self) -> etree:
        """
        Convert to an XML tree

        Returns:
            :class:`lxml.etree`: Music DB Song as XML tree
        """
        return E.mdb_data(
            __xe("music_id", self.music_id, "s32"),
            self.difficulty.to_xml(),
            __xe("pad_diff", self.pad_diff, "u16"),
            __xe("seq_flag", self.seq_flag, "u16"),
            __xe("contain_stat", " ".join(map(str, self.contain_stat)), "u8", count=2),
            __xe("b_long", "1" if self.b_long else "0", "bool"),
            __xe("b_eemall", "1" if self.b_eemall else "0", "bool"),
            __xe("bpm", self.bpm, "u16"),
            __xe("bpm2", self.bpm2, "u16"),
            __xe(
                "title_ascii",
                "".join(i for i in self.title_ascii if 31 < ord(i) < 127),
                "str",
            ),
            __xe("order_ascii", self.order_ascii, "u16"),
            __xe("order_kana", self.order_kana, "u16"),
            __xe("category_kana", self.category_kana, "s8"),
            __xe("secret", " ".join(map(str, self.secret)), "u8", count=2),
            __xe("b_session", "1" if self.b_session else "0", "bool"),
            __xe("speed", self.speed, "u8"),
            __xe("life", self.life, "u8"),
            __xe("gf_ofst", self.gf_offset, "s8"),
            __xe("dm_ofst", self.dm_offset, "s8"),
            __xe("chart_list", " ".join(map(str, self.chart_list)), "u8", count=128),
            __xe("origin", self.origin, "u8"),
            __xe("music_type", self.music_type, "u8"),
            __xe("genre", self.genre, "u8"),
            __xe("is_remaster", self.is_remaster, "u8"),
        )

    def __repr__(self) -> str:
        return (
            f"MDBSong<music_id: {self.music_id}, difficulty: {self.difficulty}, "
            f"pad_diff: {self.pad_diff}, seq_flag: {self.seq_flag}, "
            f"contain_stat: {self.contain_stat}, b_long: {self.b_long}, "
            f"b_eemall: {self.b_eemall}, bpm: {self.bpm}, bpm2: {self.bpm2}, "
            f'title_ascii: "{self.title_ascii}", order_ascii: {self.order_ascii}, '
            f"order_kana: {self.order_kana}, category_kana: {self.category_kana}, "
            f"secret: {self.secret}, b_session: {self.b_session}, speed: {self.speed}, "
            f"life: {self.life}, gf_offset: {self.gf_offset}, "
            f"dm_offset: {self.dm_offset}, chart_list: {self.chart_list}, "
            f"origin: {self.origin}, music_type: {self.music_type}, "
            f"genre: {self.genre}, is_remaster: {self.is_remaster}>"
        )


class MDBCourse(object):
    """
    Holds course data for GFDM.

    Note: This is potentially just extra unused data. V8 doesn't have courses.

    Args:
        course_id (int): Course ID
        course_flag (int): Unknown
        music_ids (List[int]): List of songs in the course
        difficulty (:class:`.MDBDifficultyList`): Difficulty list for the course
    """

    STRUCT_FORMAT = "<iI4i16B"
    """Binary data format. Used in `struct.unpack_from`"""

    def __init__(
        self,
        course_id: int,
        course_flag: int,
        music_ids: List[int],
        difficulty: MDBDifficultyList,
    ):
        self.course_id = course_id
        self.course_flag = course_flag
        self.music_ids = music_ids
        self.difficulty = difficulty

    def __repr__(self) -> str:
        return (
            f"MDBCourse<course_id: {self.course_id}, course_flag: {self.course_flag}, "
            f"music_ids: {self.music_ids}, difficulty: {self.difficulty}>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dict

        Returns:
            Dict[str, Any]: Music DB Course as a dict
        """
        return {
            "course_id": self.course_id,
            "course_flag": self.course_flag,
            "music_ids": self.music_ids,
            "difficulty": self.difficulty.to_dict(),
        }

    def to_xml(self) -> etree:
        """
        Convert to an XML tree

        Returns:
            :class:`lxml.etree`: Music DB Course as XML tree
        """
        return E.mdb_course(
            __xe("course_id", self.course_id, "s32"),
            __xe("course_flag", self.course_flag, "u32"),
            __xe("music_id", " ".join(map(str, self.music_ids)), "s32", count=4),
            self.difficulty.to_xml(),
        )

    @classmethod
    def from_byte_data(cls, data: Tuple[Any, ...]) -> MDBCourse:
        """
        Build an :class:`.MDBCourse` object from the raw bytes extracted from `mdbe.bin`

        Args:
            data (Tuple[Any, ...]): Tuple containing the unpacked data

        Returns:
            :class:`.MDBCourse`: Course object
        """
        course_id, course_flag = data[0:2]
        music_ids = data[2:6]
        diff_list = data[6:]

        # Create a proper difficulty object
        difficulty = MDBDifficultyList(
            MDBDifficulty(*diff_list[0:4]),
            MDBDifficulty(*diff_list[4:8]),
            MDBDifficulty(*diff_list[8:12]),
            MDBDifficulty(*diff_list[12:16]),
        )

        return MDBCourse(course_id, course_flag, list(music_ids), difficulty)


class MDB(object):
    """
    Given a `mdbe.bin` file path, decrypt the data, pull out any relevant info and store
    it.

    Args:
        input_path (Path): Direct path to `mdbe.bin` file
        output_path (Path): Directory to output the result to
        force (bool): Set to true to force writing the output file even if it exists
        pretty_print (bool) = False: Set to true to pretty print the output file
    """

    DECRYPTION_KEY = b"2+.58>;.A"
    """Part of the decryption process"""

    IDENTIFIER = "GF/DMmdb"
    """Identifier in the header of the file"""

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        force: bool,
        pretty_print: bool = False,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.force = force
        self.pretty_print = pretty_print
        self.decrypted_data = self.decrypt()
        self.header: Optional[MDBHeader] = None
        self.songs: Dict[int, MDBSong] = {}
        self.courses: Dict[int, MDBCourse] = {}
        self.build()

    def decrypt(self) -> bytearray:
        """
        Open up `mdbe.bin`, decrypt it and return a bytearray of the decrypted data

        Returns:
            bytearray: Decrypted data
        """
        # Read the file into memory
        input_buffer = bytearray(self.input_path.open("rb").read())

        # Allocate an output buffer and then decrypt into the output buffer
        output_buffer = bytearray(len(input_buffer))

        for cur_idx in range(0, len(input_buffer)):
            dec_byte = input_buffer[len(input_buffer) - 1 - cur_idx] ^ (
                cur_idx
                + 16 * (cur_idx % 8)
                + (
                    self.DECRYPTION_KEY[cur_idx % 9]
                    ^ (9 * (cur_idx // 9) - cur_idx + 127)
                )
                - 9 * (cur_idx // 9)
            )
            output_buffer[cur_idx] = dec_byte

        return output_buffer

    def build(self) -> None:
        """
        Using the decrypted data, build out all the header, song, and course objects

        Raises:
            Exception: If input file doesn't have the correct header id
        """
        data = self.decrypted_data

        # Read in header
        raw_header_data = data[0 : MDBHeader.DATA_SIZE]
        header_data = struct.unpack_from(MDBHeader.STRUCT_FORMAT, raw_header_data)
        self.header = MDBHeader.from_byte_data(header_data)

        # Make sure the type is correct
        if self.header.id != self.IDENTIFIER:
            raise Exception(
                f'[BAD mbde.bin FILE] Header identifier "{self.header.id}" does not '
                f'match expected identifier "{self.IDENTIFIER}"'
            )

        # Grab the song data
        # The song data size is actually 4 bytes bigger than the header would suggest
        song_data_size = self.header.record_size + 0x04

        count = 0
        start_point = MDBHeader.DATA_SIZE
        while count < self.header.record_number:
            idx_start = start_point + (song_data_size * count)
            idx_end = idx_start + song_data_size

            raw_song_data = data[idx_start:idx_end]
            song_data = struct.unpack_from(MDBSong.STRUCT_FORMAT, raw_song_data)
            song = MDBSong.from_byte_data(song_data)
            self.songs[song.music_id] = song

            count += 1

        # Grab the course data
        # The course data size is actually 4 bytes bigger than the header would suggest
        course_data_size = self.header.course_size + 0x04

        count = 0
        start_point = MDBHeader.DATA_SIZE + (
            song_data_size * (self.header.record_number)
        )
        while count < self.header.course_number:
            idx_start = start_point + (course_data_size * count)
            idx_end = idx_start + course_data_size

            raw_course_data = data[idx_start:idx_end]
            course_data = struct.unpack_from(MDBCourse.STRUCT_FORMAT, raw_course_data)
            course = MDBCourse.from_byte_data(course_data)
            self.courses[course.course_id] = course

            count += 1

    def export(self, export_type: str = "JSON") -> None:
        """
        Export the music db in the format of your choice.

        By format of your choice, I mean "XML" or "JSON".

        Args:
            export_type (str) = "JSON": Choose between "XML" and "JSON" for output type

        Raises:
            Exception: If header is emtpy
            Exception: If export format is unknown
        """
        if export_type == "JSON":
            header = self.header.to_dict() if self.header is not None else ""
            output: Dict[str, Any] = {
                "musicdb": {"header": header, "songs": {}, "courses": {}}
            }
            for key, song in self.songs.items():
                output["musicdb"]["songs"][song.music_id] = song.to_dict()
            for key, course in self.courses.items():
                output["musicdb"]["courses"][course.course_id] = course.to_dict()

            # str_output: str
            if self.pretty_print:
                str_output = json.dumps(output, indent=2).encode("UTF-8")
            else:
                str_output = json.dumps(output).encode("UTF-8")
        elif export_type == "XML":
            if self.header is None:
                raise Exception("Header is empty, could not print")

            root = E.mdb(
                self.header.to_xml(),
                *[self.songs[k].to_xml() for k in self.songs],
                *[self.courses[k].to_xml() for k in self.courses],
            )
            str_output = etree.tostring(
                root,
                xml_declaration=True,
                encoding="UTF-8",
                pretty_print=self.pretty_print,
            )
        else:
            raise Exception(f"Unknown export format: {export_type}")

        # Write output file
        filepath = self.output_path / f"mdb.{export_type.lower()}"
        if not filepath.exists() or self.force:
            print(f"Writing: {filepath}")
            filepath.open("wb").write(str_output)
        else:
            logger.error(
                f'File "{filepath}" not written. Please use `-f` to overwrite it'
            )
