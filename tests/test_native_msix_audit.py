from scripts.native_msix_audit import classify, reason


def test_gis_engines_are_separate_from_wheel_bindings():
    assert classify("_internal/fiona.libs/geos_c.dll", [{"name": "Fiona"}]) == ("geos", "GEOS")
    assert classify("_internal/pyproj.libs/proj_9_7.dll", [{"name": "pyproj"}]) == ("proj", "PROJ")
    assert classify("_internal/fiona/ogrext.pyd", [{"name": "Fiona"}])[0] == "gdal"
    assert classify("_internal/shapely/lib.pyd", [{"name": "Shapely"}])[0] == "geos"


def test_own_qt_numpy_python_and_unknown_are_not_misrepresented():
    assert classify("AgroLinesPoC.exe", [])[0] == "own"
    assert classify("_internal/PySide6/Qt6Core.dll", [{"name": "PySide6_Essentials"}])[0] == "qt"
    assert classify("_internal/numpy.libs/openblas.dll", [{"name": "numpy"}]) == (
        "numpy",
        "OpenBLAS",
    )
    assert classify("_internal/python312.dll", [{"name": "CPython"}])[0] == "python"
    assert classify("_internal/unrecognized.dll", [])[0] == "other"


def test_valid_authenticode_with_expired_current_chain_is_not_rejection():
    signature = {"status": "Valid", "chain_valid": False, "chain_status": ["NotTimeValid"]}
    message = reason(signature, {"exit_code": 0})
    assert "Windows Authenticode accepted" in message
    assert "NotTimeValid" in message and "do not infer SAC rejection" in message


def test_unsigned_and_inconclusive_remain_unapproved():
    assert "No Authenticode" in reason({"status": "NotSigned"}, {"exit_code": 1})
    signature = {
        "status": "UnknownError",
        "chain_valid": False,
        "chain_status": ["OfflineRevocation"],
        "status_message": "Revocation unavailable",
    }
    message = reason(signature, {"exit_code": None})
    assert "failed/inconclusive" in message and "OfflineRevocation" in message
