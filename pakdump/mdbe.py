from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from lxml import etree
from lxml.builder import E


def xe(name: str, body: Any, type: str, count: int = 1) -> E:
    attrs = {"__type": type}
    if count > 1:
        attrs["__count"] = str(count)
    return E(name, str(body), attrs)


class MDBHeader(object):
    STRUCT_FORMAT = "<8b2i5h"
    DATA_SIZE = 0x40

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

    @classmethod
    def from_byte_data(self, data: Tuple[Any, ...]) -> MDBHeader:
        id = bytes(data[0:8]).decode("UTF-8")
        (
            format,
            checksum,
            header_size,
            record_size,
            record_number,
            course_size,
            course_number,
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

    def to_dict(self) -> Dict[str, Any]:
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
        return E.header(
            E.data(
                xe(
                    "id", " ".join(map(str, bytearray(self.id, "UTF-8"))), "s8", count=8
                ),
                xe("format", self.format, "s32"),
                xe("chksum", self.checksum, "s32"),
                xe("header_sz", self.header_size, "s16"),
                xe("record_sz", self.record_size, "s16"),
                xe("record_nr", self.record_number, "s16"),
                xe("course_sz", self.course_size, "s16"),
                xe("course_nr", self.course_number, "s16"),
            )
        )

    def __repr__(self) -> str:
        return (
            f'MDBHeader<id: "{self.id}", format: {self.format}, '
            f"checksum: {self.checksum}, header_size: {self.header_size}, "
            f"record_size: {self.record_size}, record_number: {self.record_number}, "
            f"course_size: {self.course_size}, course_number: {self.course_number}>"
        )


# Beg, Bas, Adv, Ext
# Guitar -> Bass -> Open -> Drum
# 0, 52, 70, 89 -> 0, 46, 69, 81 -> 0, 54, 73, 90 -> 0, 48, 76, 86


class MDBSongDifficulty(object):
    def __init__(self, beginner: int, basic: int, advanced: int, extreme: int) -> None:
        self.beginner = beginner
        self.basic = basic
        self.advanced = advanced
        self.extreme = extreme

    def __repr__(self) -> str:
        return (
            f"MDBSongDifficulty<beginner: {self.beginner}, basic: {self.basic}, "
            f"advanced: {self.advanced}, extreme: {self.extreme}>"
        )


class MDBSongDifficultyList(object):
    def __init__(
        self,
        guitar: MDBSongDifficulty,
        bass: MDBSongDifficulty,
        open_pick: MDBSongDifficulty,
        drum: MDBSongDifficulty,
    ) -> None:
        self.guitar = guitar
        self.bass = bass
        self.open_pick = open_pick
        self.drum = drum

    def __repr__(self) -> str:
        return (
            f"MDBSongDifficultyList<guitar: {self.guitar}, bass: {self.bass}, "
            f"open_pick: {self.open_pick}, drum: {self.drum}>"
        )


class MDBSongChartList(object):
    def __init__(self):
        pass


class MDBSong(object):
    STRUCT_FORMAT = "<i16BHH2BBBHH16BHHB2BBBBbb128BBBBB"

    def __init__(
        self,
        music_id: int,
        difficulty_list: MDBSongDifficultyList,
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
        char_list: MDBSongChartList,
        origin: int,
        music_type: int,
        genre: int,
        is_remaster: int,
    ):
        pass

    @classmethod
    def from_byte_data(self, data: bytes) -> MDBSong:
        pass


class MDBCourse(object):
    def __init__(self):
        pass

    @classmethod
    def from_byte_data(self, data: bytes) -> MDBCourse:
        pass


class MDB(object):
    """
    Given a `mdbe.bin` file path, decrypt the data, pull out any relevant info and store
    it.
    """

    DECRYPTION_KEY = b"2+.58>;.A"
    IDENTIFIER = "GF/DMmdb"

    def __init__(self, input_path: Path) -> None:
        self.input_path = input_path
        self.decrypted_data = self.decrypt()
        self.header: Optional[MDBHeader] = None
        self.songs: Dict[int, MDBSong] = {}
        self.courses: Dict[int, MDBCourse] = {}
        self.build()

    def decrypt(self) -> bytearray:
        """
        Open up `mdbe.bin`, decrypt it and return a bytearray of the decrypted data
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

        # The song data size is actually 4 bytes bigger than the header would suggest
        song_data_size = self.header.record_size + 0x04

        count = 0
        while count < self.header.record_number:
            idx_start = MDBHeader.DATA_SIZE + (song_data_size * count)
            idx_end = idx_start + song_data_size

            raw_song_data = data[idx_start:idx_end]
            song_data = struct.unpack_from(MDBSong.STRUCT_FORMAT, raw_song_data)
            song = MDBSong.from_byte_data(song_data)

            count += 1

    def export(self, export_type: str = "JSON") -> None:
        """
        Export the music db in the format of your choice.

        By format of your choice, I mean "XML" or "JSON".
        """
        if export_type == "JSON":
            header = self.header.to_dict() if self.header is not None else ""
            output = {"musicdb": {"header": header}}

            print(json.dumps(output, indent=2))
        elif export_type == "XML":
            pass
            # print(etree.tostring(header.as_xml(), pretty_print=True).decode("UTF-8"))
        else:
            raise Exception(f"Unknown export format: {export_type}")
