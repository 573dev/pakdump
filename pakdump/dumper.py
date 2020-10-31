import hashlib
import logging
import re
import struct
from ctypes import c_ulong
from pathlib import Path
from typing import Any, Dict, List, Optional

import pakdec
from pakdump.crc import CRC16_CCITT_TABLE_REVERSE


logger = logging.getLogger(__name__)
"""pakdump.dumper log object"""


class PackInfo(object):
    """
    Contains all the information for a single entry in the Packinfo.bin file

    Args:
        crc32 (int): CRC32 Checksum
        crc16 (int): CRC16 Checksum
        packid (int): ID for the pack file that this data is contained in
        offset (int): File offset in bytes for where to find the data
        filesize (int): Size of the file in bytes
        md5sum (int): MD5 sum of the file
    """

    def __init__(
        self,
        crc32: int,
        crc16: int,
        packid: int,
        offset: int,
        filesize: int,
        md5sum: bytes,
    ) -> None:
        self.crc32 = crc32
        self.crc16 = crc16
        self.packid = packid
        self.offset = offset
        self.filesize = filesize
        self.md5sum = md5sum.hex()
        self.filename = None  # Gets filled in later

    def __repr__(self) -> str:
        return (
            f"PackInfo<crc32: {self.crc32}, crc16: {self.crc16}, "
            f"packid: {self.packid}, offset: {self.offset}, filesize: {self.filesize}, "
            f'md5sum: {self.md5sum}, filename: "{self.filename}">'
        )


class PakDumper(object):
    """
    Keeps track of all the input/output paths, as well as all the info in the pack
    files.

    Generate entries, calculate CRC values, and extract data.

    Args:
        inputpath (Path): Path to `data` directory
        outputpath (Path): Path to output directory
        force (bool): Set to true to overwrite extracted files even if they exist
    """

    def __init__(self, inputpath: Path, outputpath: Path, force: bool) -> None:
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.packinfo_path = self.find_pakinfo()
        self.entries = self.parse_pack_data()
        self.packlist = self.generate_packlist()
        self.crc32_table = self.generate_crc32_table()
        self.force = force

    def get_md5sum(self, data: bytearray) -> str:
        """
        Generate and return the MD5 sum for data extracted from the pack files.

        This is used to confirm that the data has been pulled out properly. This serves
        a secondary purpose to check if the extracted data needs to be de-crypted or not

        Args:
            data (bytearray): File data to calculate the MD5 hash for

        Returns:
            str: MD5 hash
        """
        md5 = hashlib.md5()
        md5.update(data)
        return md5.digest().hex()

    def decrypt(self, data: bytearray, entry: PackInfo) -> bytearray:
        """
        Decrypt extracted data

        Using pakdec (a Cython module) for fast decryption

        Args:
            data (bytearray): Byte data to decrypt
            entry (:class:`.PackInfo`): PakInfo object with necessary data required for
                decryption

        Returns:
            bytearray: Decrypted data
        """
        pakdec.decrypt(data, len(data), entry.crc32, entry.crc16)
        return data

    def extract_data_mem(self, key: int) -> Optional[bytearray]:
        """
        Extract the requested data out of the pack files. Decrypt if necessary.

        Args:
            key (int): Filename key of file to extract

        Returns:
            Optional[bytearray]: Extracted data or None if it can't be found
        """

        entry = self.entries[key]

        # Make sure the packid exists in the packlist
        if entry.packid not in self.packlist:
            logger.error(f"[BAD PACK_ID] {entry}")
            return None

        # Get the pack path and make sure it exists
        packpath = self.inputpath / self.packlist[entry.packid]
        if not packpath.exists():
            logger.error(f"Packpath does not exist: {packpath}")
            return None

        # Grab the data from the pack
        logger.debug(f"Loading packpath: {packpath}")
        data = bytearray(
            packpath.open("rb").read()[entry.offset : entry.offset + entry.filesize]
        )

        # If the data is encrypted, lets decrypt it
        data_md5 = self.get_md5sum(data)
        if data_md5 != entry.md5sum:
            logger.debug(f"Decrypting file: {entry.filename}")
            data = self.decrypt(data, entry)

        # Make sure the md5sum matches
        data_md5 = self.get_md5sum(data)
        if data_md5 != entry.md5sum:
            logger.error(f'MD5 sum "{data_md5}" does not match "{entry.md5sum}"')
            return None

        return data

    def extract_data(self, key: int) -> None:
        """
        Given the file hash key, extract the data and write it to the output dir

        Args:
            key (int): Filename key of file to extract
        """
        data = self.extract_data_mem(key)

        if data is None:
            logger.error(f"Could not extract data from: {self.entries[key].filename}")
            return

        # Write the data
        filepath = self.entries[key].filename
        filepath = filepath[1:] if filepath.startswith("/") else filepath
        output_path = self.outputpath / filepath
        logger.debug(f"Writing: {output_path}")

        # Make sure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Only write the data if it doesn't already exist
        if output_path.exists() and not self.force:
            logger.info(f"File already exists: {output_path}")
            return

        output_path.open("wb").write(data)

    def dump(self) -> None:
        """
        Dump the data
        """
        sorted_keys = sorted(
            self.entries, key=lambda x: (self.entries[x].packid, self.entries[x].offset)
        )

        extracted = 0
        for key in sorted_keys:
            entry = self.entries[key]
            if entry.filename is not None:
                logger.info(f"Extracting File: {entry.filename}")
                self.extract_data(key)
                extracted += 1

        logger.info(f"Extracted {extracted} files.")
        logger.info(f"{len(self.entries) - extracted} files remaining.")

    def file_exists(self, filepath: Path) -> bool:
        """
        Determine if the filename exists in the pack data.
        Add the filename to the entry if we find a match.

        Args:
            filepath (Path): Filepath to check

        Returns:
            bool: True if file exists in the data
        """
        crc32 = self.calculate_filename_crc32(filepath)
        crc16 = self.calculate_filename_crc16(filepath)
        exists = crc32 in self.entries and self.entries[crc32].crc16 == crc16

        if exists:
            self.entries[crc32].filename = str(filepath)
        else:
            logger.error(f"Filepath does not exist: {filepath}")

        return exists

    def calculate_filename_crc16(self, filename: Path) -> int:
        """
        Calculate the crc16 filename hash

        Args:
            filename (Path): Filepath to create the CRC16 for

        Returns:
            int: CRC16 for filename
        """
        filebytes = bytearray(str(filename), "ASCII")
        crc16 = 0xFFFF
        for b in filebytes:
            crc16 = (
                (crc16 >> 8) ^ CRC16_CCITT_TABLE_REVERSE[(crc16 ^ b) & 0x00FF]
            ) & 0xFFFF

        return ~crc16 & 0xFFFF

    def calculate_filename_crc32(self, filename: Path) -> int:
        """
        Calculate the crc32 filename hash
        Args:
            filename (Path): Filepath to create the CRC32 for

        Returns:
            int: CRC32 for filename
        """
        # Normalize paths to proper formats
        filestr = str(filename)

        # Make sure we have a leading '/'
        filestr = "/" + filestr if filestr.startswith("data/") else filestr

        # /data/aep paths should be lowercase
        filestr = filestr.lower() if filestr.startswith("/data/aep") else filestr

        # Calculate crc32
        filebytes = bytearray(filestr, "ASCII")
        crc32_sum = 0xFFFFFFFF
        for i in range(len(filebytes)):
            crc32_sum = self.crc32_table[(crc32_sum & 0xFF) ^ filebytes[i]] ^ (
                (crc32_sum >> 8) & 0xFFFFFFFF
            )
        return ~crc32_sum & 0xFFFFFFFF

    def generate_crc32_table(self) -> List[int]:
        """
        Generate a crc32 table. Used fo calculating the filename hash

        I'm not really sure exactly how this was determined

        Returns:
            List[int]: CRC32 table
        """
        crc32_table = []
        crc32_constant = 0xEDB88320

        for i in range(0, 256):
            crc = i
            for j in range(0, 8):
                if crc & 0x00000001:
                    crc = int(c_ulong(crc >> 1).value) ^ crc32_constant
                else:
                    crc = int(c_ulong(crc >> 1).value)
            crc32_table.append(crc)
        return crc32_table

    def generate_packlist(self) -> Dict[int, Path]:
        """
        Glob through the data folder to find any files matching `packXXXX.pak`

        Returns:
            Dict[int, Path]: Packid with path
        """
        packlist = list(self.inputpath.glob("**/pack*.pak"))

        # Grab the packid
        items: Dict[int, Path] = {}
        for pack in packlist:
            r = re.match(r"pack(?P<id>\d\d\d\d).pak", pack.parts[-1])
            if r is None:
                logger.error("Packpath is malformed: {pack}")
                continue
            pak_id = int(r.group("id"))
            items[pak_id] = pack

        return items

    def parse_pack_data(self) -> Dict[int, Any]:
        """
        Parse the data from packinfo.bin

        Returns:
            Dict[int, Any]: Data dictionary pulled out of the packinfo file
        """
        entries: Dict[int, Any] = {}

        with self.packinfo_path.open("rb") as f:
            f.seek(0x08)
            end_address = int.from_bytes(f.read(0x04), "little")
            f.seek(0x10)

            while f.tell() < end_address:
                md5sum = f.read(0x10)
                data = f.read(0x10)

                if not md5sum or not data:
                    break

                crc32, crc16, packid, offset, filesize = struct.unpack("<IHHII", data)
                entry = PackInfo(crc32, crc16, packid, offset, filesize, md5sum)

                if crc32 in entries and entries[crc32].crc16 == crc16:
                    logger.debug(f"Found key already: {entries[crc32]}")
                    continue

                entries[crc32] = entry
        return entries

    def find_pakinfo(self) -> Path:
        """
        Find the `packinfo.bin` file. It is expected to be in `data/pack/packinfo.bin`,
        but we will search the whole sub tree for it.

        Returns:
            Path: Path to the pakinfo.bin file
        """
        logger.debug(f"Searching for `packinfo.bin` in subtree: {self.inputpath}")
        infopaths = list(self.inputpath.glob("**/packinfo.bin"))
        count = len(infopaths)

        if count == 0:
            raise Exception(
                f"Couln't find packinfo.bin in the subtree: {self.inputpath}"
            )

        # There shouldn't be more than one of these files, but if there is then just
        # grab the last one
        infopath = infopaths[-1]
        logger.debug(f"Found packinfo at: {infopath}")

        return infopath
