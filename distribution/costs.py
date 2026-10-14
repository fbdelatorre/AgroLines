"""Optional current public Azure retail prices; never invent a quote on network failure."""

import argparse
import json
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    url = "https://prices.azure.com/api/retail/prices?" + urllib.parse.urlencode(
        {
            "currencyCode": "USD",
            "$filter": "serviceName eq 'Artifact Signing' or serviceName eq 'Trusted Signing'",
        }
    )
    report = {"source": url, "retrieved_utc": datetime.now(UTC).isoformat(), "verified_prices": []}
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.load(response)
        if data.get("NextPageLink"):
            raise ValueError("Incomplete price page; obtain complete official quote")
        fields = [
            "productName",
            "skuName",
            "meterName",
            "retailPrice",
            "unitOfMeasure",
            "currencyCode",
            "armRegionName",
            "effectiveStartDate",
        ]
        report["verified_prices"] = [{k: item.get(k) for k in fields} for item in data["Items"]]
        report["status"] = "retrieved" if report["verified_prices"] else "no_matching_prices"
    except Exception as error:
        report["status"] = "unavailable"
        report["error_type"] = type(error).__name__
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = json.dumps({"status": report["status"], "prices": report["verified_prices"][:8]})
    print("::notice title=Public signing prices (informative)::" + summary)


if __name__ == "__main__":
    main()
