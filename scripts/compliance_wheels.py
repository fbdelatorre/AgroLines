"""Read PE constants from hash-pinned vendor wheels; never load or execute native code."""

import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

import pefile

EXPORTS = {
    "spatialite_version",
    "freexl_version",
    "json_c_version",
    "nc_inq_libvers",
    "opj_version",
    "TIFFGetVersion",
    "png_get_libpng_ver",
    "ZSTD_versionString",
    "zlibVersion",
    "qh_version",
    "WebPGetDecoderVersion",
    "SZ_encoder_enabled",
}


def inspect(wheel, expected_sha, native):
    with Path(wheel).open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected_sha:
            raise ValueError("Vendor wheel hash mismatch")
    known = {r["path"].removeprefix("_internal/").casefold(): r for r in native}
    records = []
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            row = known.get(name.casefold())
            if not row:
                continue
            raw = archive.read(name)
            digest = hashlib.sha256(raw).hexdigest()
            if digest != row["sha256"]:
                raise ValueError("Wheel member does not match distributed PE")
            with pefile.PE(data=raw, fast_load=False) as binary:
                exports = []
                directory = getattr(binary, "DIRECTORY_ENTRY_EXPORT", None)
                for entry in directory.symbols if directory else []:
                    symbol = entry.name.decode("ascii") if entry.name else ""
                    if symbol not in EXPORTS:
                        continue
                    code = binary.get_data(entry.address, 16)
                    value, method = None, "unrecognized; not executed"
                    if code[:3] in (b"\x48\x8d\x05", b"\x48\x8b\x05") and code[7] == 0xC3:
                        rva = entry.address + 7 + struct.unpack("<i", code[3:7])[0]
                        if code[1] == 0x8B:
                            rva = struct.unpack("<Q", binary.get_data(rva, 8))[0]
                            rva -= binary.OPTIONAL_HEADER.ImageBase
                        value = binary.get_string_at_rva(rva).decode("ascii", errors="strict")
                        method = "x64 leaf function returns constant string; static inspection"
                    elif code[0] == 0xB8 and code[5] == 0xC3:
                        value = struct.unpack("<I", code[1:5])[0]
                        method = "x64 leaf function returns constant integer; static inspection"
                    elif symbol == "qh_version":
                        value = binary.get_string_at_rva(entry.address).decode("ascii")
                        method = "exported constant data; static inspection"
                    exports.append(
                        {
                            "export": symbol,
                            "value": value,
                            "method": method,
                            "initial_bytes_hex": code.hex(),
                        }
                    )
                records.append(
                    {
                        "path": row["path"],
                        "sha256": digest,
                        "wheel_member": name,
                        "constants": exports,
                    }
                )
    return {
        "wheel": Path(wheel).name,
        "wheel_sha256": expected_sha,
        "files": records,
        "native_code_executed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    native = json.loads(Path("docs/compliance/evidence/native.json").read_text())
    args.output.write_text(json.dumps(inspect(args.wheel, args.sha256, native), indent=2) + "\n")


if __name__ == "__main__":
    main()
