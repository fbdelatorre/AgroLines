"""Read public upstream source/legal materials only. No install, build or signing."""

import base64
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

OUTPUT = Path("build/legal-upstream")
SOURCES = {
    "libiconv-1.17": "https://ftp.gnu.org/gnu/libiconv/libiconv-1.17.tar.gz",
    "freexl-2.0.0": "https://www.gaia-gis.it/gaia-sins/freexl-2.0.0.tar.gz",
    "spatialite-5.1.0": "https://www.gaia-gis.it/gaia-sins/libspatialite-sources/libspatialite-5.1.0.tar.gz",
    "geos-3.14.1": "https://download.osgeo.org/geos/geos-3.14.1.tar.bz2",
}
EXPECTED = {
    # Official vcpkg baseline declared by the Fiona Windows build recipe.
    "libiconv-1.17": "18a09de2d026da4f2d8b858517b0f26d853b21179cf4fa9a41070b2d140030ad9525637dc4f34fc7f27abca8acdc84c6751dfb1d426e78bf92af4040603ced86",
    "freexl-2.0.0": "663ccc321c2f0dcab8ad9255b2a77066c2046d531a0aa723fb114301fa27b53bf980787dd2548c46541036eceef988c5eedf2bec053adf628929470e67ddc17a",
    "spatialite-5.1.0": "2745b373e31cea58623224def6090c491b58409803bb71231450dfa2cfdf3aafc3fc6f680585d55d085008f8cf362c3062ae67ffc7d80257775a22eb81ef1e57",
}


def fetch(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "AgroLines-legal-materials-read-only/1"}
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        if response.url.split(":", 1)[0] != "https":
            raise ValueError("No insecure redirect accepted")
        return response.read()


def main():
    OUTPUT.mkdir(parents=True)
    results = []
    for name, url in SOURCES.items():
        row = {
            "component": name,
            "url": url,
            "source_binary_correspondence": False,
            "documents": [],
        }
        try:
            archive = fetch(url)
            row.update(
                sha256=hashlib.sha256(archive).hexdigest(),
                sha512=hashlib.sha512(archive).hexdigest(),
                size_bytes=len(archive),
            )
            if name in EXPECTED and row["sha512"] != EXPECTED[name]:
                raise ValueError("Official source differs from pinned vcpkg recipe input")
            row["declared_source_input_checksum_matched"] = name in EXPECTED
            destination = OUTPUT / "sources" / url.rsplit("/", 1)[-1]
            destination.parent.mkdir(exist_ok=True)
            destination.write_bytes(archive)
            row["archive_file"] = destination.relative_to(OUTPUT).as_posix()
            with tarfile.open(fileobj=io.BytesIO(archive)) as package:
                for member in package.getmembers():
                    path = Path(member.name)
                    if (
                        not member.isfile()
                        or len(path.parts) > 3
                        or not re.match(
                            r"^(COPYING|LICENSE|LICENCE|NOTICE|AUTHORS|COPYRIGHT)([.\-_].*)?$",
                            path.name,
                            re.I,
                        )
                    ):
                        continue
                    data = package.extractfile(member).read()
                    if len(data) > 200_000:
                        raise ValueError("Unexpected legal document size")
                    filename = name + "--" + member.name.replace("/", "__")
                    (OUTPUT / filename).write_bytes(data)
                    document = {
                        "archive_member": member.name,
                        "filename": filename,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "bytes": len(data),
                    }
                    row["documents"].append(document)
                    # Original public notices only; no source objects, credentials or binaries.
                    print(
                        "AGROLINES_UPSTREAM_DOCUMENT="
                        + json.dumps(
                            {
                                **document,
                                "component": name,
                                "content_base64": base64.b64encode(data).decode(),
                            }
                        )
                    )
            row["status"] = "downloaded_source_and_extracted_original_notices"
        except Exception as exc:
            row.update(status="unavailable", error=str(exc))
        results.append(row)
    report = {
        "sources": results,
        "legal_approved": False,
        "source_offer_complete": False,
        "installation_performed": False,
    }
    (OUTPUT / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print("AGROLINES_UPSTREAM_RESULTS=" + json.dumps(report))


if __name__ == "__main__":
    main()
