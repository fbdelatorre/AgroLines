# SPDX-License-Identifier: 0BSD
"""Synthetic HDF5/SZIP interop; original SZIP is READ ONLY, never encodes."""

import argparse
import ctypes as c
import hashlib
import json
import os
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prefix", type=Path, required=True)
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--write-with-bsd-codec", action="store_true")
    args = p.parse_args()
    if (
        sys.platform != "win32"
        or sys.getwindowsversion().product_type == 1
        or os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
    ):
        raise RuntimeError("Isolated authorized Windows Server builder required")
    sys.path.insert(0, str(args.prefix.resolve()))
    import fiona

    if not Path(fiona.__file__).resolve().is_relative_to(args.prefix.resolve()):
        raise RuntimeError("Wrong Fiona copy")
    libs = args.prefix / "fiona.libs"
    path = next(libs.glob("hdf5-*.dll"))
    # Fiona/GDAL has already loaded its dependency; never select another codec.
    kernel = c.WinDLL("kernel32", use_last_error=True)
    kernel.GetModuleHandleW.argtypes = [c.c_wchar_p]
    kernel.GetModuleHandleW.restype = c.c_void_p
    kernel.GetProcAddress.argtypes = [c.c_void_p, c.c_char_p]
    kernel.GetProcAddress.restype = c.c_void_p
    kernel.GetModuleFileNameW.argtypes = [c.c_void_p, c.c_wchar_p, c.c_uint]
    kernel.GetModuleFileNameW.restype = c.c_uint

    def loaded_path(expected):
        module = kernel.GetModuleHandleW(expected.name)
        value = c.create_unicode_buffer(32768)
        if not module or not kernel.GetModuleFileNameW(module, value, len(value)):
            raise RuntimeError("Expected native module was not loaded")
        actual = Path(value.value).resolve()
        if actual != expected.resolve():
            raise RuntimeError("Loaded native module came from another installation")
        return actual

    path = loaded_path(path)
    handle = kernel.GetModuleHandleW(path.name)
    if not handle:
        raise RuntimeError("Expected vendor HDF5 was not loaded")

    def fn(name, restype, *types):
        address = kernel.GetProcAddress(handle, name.encode())
        if not address:
            raise RuntimeError("Missing HDF5 export " + name)
        return c.CFUNCTYPE(restype, *types)(address)

    hid = c.c_int64

    def gid(name):
        address = kernel.GetProcAddress(handle, name.encode())
        if not address:
            raise RuntimeError("Missing HDF5 type " + name)
        return hid.from_address(address).value

    def okay(value):
        if value < 0:
            raise RuntimeError("HDF5 operation failed")
        return value

    okay(fn("H5open", c.c_int)())
    create = fn("H5Fcreate", hid, c.c_char_p, c.c_uint, hid, hid)
    fopen = fn("H5Fopen", hid, c.c_char_p, c.c_uint, hid)
    close = fn("H5Fclose", c.c_int, hid)
    dclose = fn("H5Dclose", c.c_int, hid)
    file = okay(
        create(os.fsencode(args.file), 2, 0, 0)
        if args.write_with_bsd_codec
        else fopen(os.fsencode(args.file), 0, 0)
    )
    cases = []
    specs = [
        ("u8", "H5T_STD_U8LE_g", "H5T_NATIVE_UCHAR_g", c.c_ubyte),
        ("u16", "H5T_STD_U16LE_g", "H5T_NATIVE_USHORT_g", c.c_ushort),
        ("u32", "H5T_STD_U32LE_g", "H5T_NATIVE_UINT_g", c.c_uint),
        ("f64", "H5T_IEEE_F64LE_g", "H5T_NATIVE_DOUBLE_g", c.c_double),
    ]
    try:
        for label, stored, native, scalar in specs:
            for mask in (4, 32):
                name = f"{label}_{mask}".encode()
                values = [i % 16 if label != "f64" else (i % 16) * 0.5 for i in range(2048)]
                source = (scalar * len(values))(*values)
                expected = bytes(source)
                if args.write_with_bsd_codec:
                    space = okay(
                        fn("H5Screate_simple", hid, c.c_int, c.POINTER(c.c_uint64), c.c_void_p)(
                            2, (c.c_uint64 * 2)(32, 64), None
                        )
                    )
                    prop = okay(fn("H5Pcreate", hid, hid)(gid("H5P_CLS_DATASET_CREATE_ID_g")))
                    okay(
                        fn("H5Pset_chunk", c.c_int, hid, c.c_int, c.POINTER(c.c_uint64))(
                            prop, 2, (c.c_uint64 * 2)(16, 32)
                        )
                    )
                    okay(fn("H5Pset_szip", c.c_int, hid, c.c_uint, c.c_uint)(prop, mask, 8))
                    data = okay(
                        fn("H5Dcreate2", hid, hid, c.c_char_p, hid, hid, hid, hid, hid)(
                            file, name, gid(stored), space, 0, prop, 0
                        )
                    )
                    okay(
                        fn("H5Dwrite", c.c_int, hid, hid, hid, hid, hid, c.c_void_p)(
                            data, gid(native), 0, 0, 0, source
                        )
                    )
                    okay(fn("H5Pclose", c.c_int, hid)(prop))
                    okay(fn("H5Sclose", c.c_int, hid)(space))
                    okay(dclose(data))
                data = okay(fn("H5Dopen2", hid, hid, c.c_char_p, hid)(file, name, 0))
                try:
                    result = (scalar * len(values))()
                    okay(
                        fn("H5Dread", c.c_int, hid, hid, hid, hid, hid, c.c_void_p)(
                            data, gid(native), 0, 0, 0, result
                        )
                    )
                    if bytes(result) != expected:
                        raise RuntimeError("HDF5/SZIP roundtrip changed bytes")
                    storage = fn("H5Dget_storage_size", c.c_uint64, hid)(data)
                    if not 0 < storage < len(expected):
                        raise RuntimeError("Fixture did not exercise actual compressed storage")
                    cases.append(
                        {
                            "type": label,
                            "options": mask,
                            "raw_bytes": len(expected),
                            "stored_bytes": storage,
                            "exact_bytes": True,
                        }
                    )
                finally:
                    okay(dclose(data))
    finally:
        okay(close(file))
    codec = loaded_path(next(libs.glob("szip-*.dll")))
    report = {
        "cases": cases,
        "hdf5_path": str(path),
        "hdf5_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "codec_path": str(codec),
        "codec_sha256": hashlib.sha256(codec.read_bytes()).hexdigest(),
        "original_szip_encoder_executed": False,
        "bsd_codec_wrote_fixture": args.write_with_bsd_codec,
        "passed": True,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("AGROLINES_SZIP_INTEROP=" + json.dumps(report))


if __name__ == "__main__":
    main()
