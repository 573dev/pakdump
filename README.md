# V8 Pak Dump
[![Build Status](https://github.com/573dev/pakdump/workflows/build/badge.svg)](https://github.com/573dev/pakdump/actions?query=workflow:build)
[![Documentation Status](https://readthedocs.org/projects/pakdump/badge/?version=latest)](https://pakdump.readthedocs.io/en/latest/?badge=latest)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Dump the data from .pak files for GFDM V8

## Usage

I decided not to push this to PyPI for now, so if you want to use it you can just install it into a virtualenv like so:

```sh
cd pakdump
python -m venv venv
. venv/bin/activate

pip install --upgrade pip
pip install -e .
```

Then you can use the two commands: `pakdump` and `mdbdump`.
Please see the documentation for more information.

## pakdump

Extract files from the GFDM V8 data files.

## mdbdump

Decrypt and extract the data out of the `mbde.bin` data file which can be extracted from the data files with `pakdump`.

## mdbcreate

Read in JSON encoded MusicDB data, encrypt it and dump it into the binary `mdbe.bin` format.


### MusicDB Modification

First you want to decrypt your `mdbe.bin` file with mdbdump:

```
$ mdbdump -i mdbe.bin -o . -f -t JSON -p
Writing: /Users/573dev/Documents/pakdump/mdb.json
```

Then you can open up `mdb.json` and modify it to your hearts content. When you are done, and want to convert it back into `mdbe.bin` you can use mdbcreate:

```
$ mdbcreate -i mdb.json -o mdbe_new.bin -f
Writing: /Users/573dev/Documents/pakdump/mdbe_new.bin
```

Now just replace the original `mdbe.bin` with the new `mdbe_new.bin` (remember to rename it to `mdbe.bin`) and you should be good to go.

## License

pakdump is provided under an MIT License.
