#!/usr/bin/env python3

"""
Collect data from PGOBBAddrMap and generate same CSV as mbb-profile-dump.

Ensure that the ELF being measured has the pgo-bb-addr-map enabled. The
following flags should be enough to generate the data:
`-fbasic-block-sections=labels -mllvm --pgo-bb-addr-map=func-entry-count,bb-freq`
"""

import argparse
import json
import subprocess
import sys


def load_addrmaps(object: str) -> list:
    """Loads from a pre-generated json file or read object using readobj"""
    if object.endswith(".json"):
        with open(object) as f:
            readobj_dict: dict = json.load(f)
    else:
        readobj_dump: str = subprocess.check_output(
            [
                "llvm-readobj",
                "--pgo-bb-addr-map",
                object,
                "--elf-output-style=JSON",
            ]
        ).decode("utf-8")
        readobj_dict: dict = json.loads(readobj_dump)
    return readobj_dict[0]["PGOBBAddrMap"]


def print_csv_rows(addrmaps: list):
    """Iterates basic blocks to print function, ID, and absolute block frequency"""
    for addrmap in addrmaps:
        function: dict = addrmap["Function"]
        bb_entries: list = function["BB entries"]
        if not bb_entries:
            continue
        entry_count: float = float(function["EntryCount"])
        entry_freq: float = bb_entries[0]["Frequency"]
        for block in bb_entries:
            block_freq: float = float(block["Frequency"])
            rel_block_freq: float = block_freq / entry_freq
            abs_block_freq: float = rel_block_freq * entry_count
            print(
                function["Name"],
                block["ID"],
                abs_block_freq,
                sep=",",
            )


def main() -> int:
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument(
        "object",
        type=str,
        help="path to either an ELF compiled with pgo-bb-addr-map or a pre-generated JSON from an ELF",
    )
    object: str = argp.parse_args().object
    addrmaps: list = load_addrmaps(object)
    print_csv_rows(addrmaps)
    return 0


if __name__ == "__main__":
    sys.exit(main())

