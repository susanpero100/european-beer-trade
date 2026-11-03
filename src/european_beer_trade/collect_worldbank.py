import json
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "data" / "raw" / "worldbank"

INDICATORS = {
    "population": "SP.POP.TOTL",
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
}

EU27 = [
    "AUT",
    "BEL",
    "BGR",
    "HRV",
    "CYP",
    "CZE",
    "DNK",
    "EST",
    "FIN",
    "FRA",
    "DEU",
    "GRC",
    "HUN",
    "IRL",
    "ITA",
    "LVA",
    "LTU",
    "LUX",
    "MLT",
    "NLD",
    "POL",
    "PRT",
    "ROU",
    "SVK",
    "SVN",
    "ESP",
    "SWE",
]

API_BASE = "https://api.worldbank.org/v2/country"
EXPECTED_RECORDS = len(EU27) * 7


def fetch_page(
    session: requests.Session,
    url: str,
    page: int,
) -> requests.Response:
    params: dict[str, str | int] = {
        "format": "json",
        "date": "2019:2025",
        "per_page": 50,
        "page": page,
    }

    for attempt in range(3):
        try:
            response = session.get(
                url,
                params=params,
                timeout=60,
            )
            response.raise_for_status()
            return response

        except requests.RequestException:
            if attempt == 2:
                raise

            time.sleep(2**attempt)

    raise RuntimeError("Request failed")


def collect_indicator(
    session: requests.Session,
    name: str,
    code: str,
) -> None:
    url = f"{API_BASE}/{';'.join(EU27)}/indicator/{code}"

    all_records: list[dict] = []
    urls: list[str] = []

    page = 1
    total_pages = 1

    while page <= total_pages:
        response = fetch_page(session, url, page)
        payload = response.json()

        if not isinstance(payload, list) or len(payload) != 2:
            raise ValueError("Unexpected API response")

        metadata, records = payload

        if not isinstance(records, list):
            raise TypeError("Invalid records")

        total_pages = int(metadata["pages"])
        all_records.extend(records)
        urls.append(response.url)

        print(f"{name}: page {page}/{total_pages}")
        page += 1

    if len(all_records) != EXPECTED_RECORDS:
        raise ValueError(
            f"{name}: expected {EXPECTED_RECORDS} records, received {len(all_records)}"
        )

    countries = {record["countryiso3code"] for record in all_records}

    if countries != set(EU27):
        raise ValueError("Unexpected country coverage")

    keys = [(record["countryiso3code"], record["date"]) for record in all_records]

    if len(set(keys)) != EXPECTED_RECORDS:
        raise ValueError("Duplicate or missing country-year keys")

    snapshot = {
        "source": "World Bank API",
        "indicator": code,
        "url": urls[0],
        "request_urls": urls,
        "extracted_at": datetime.now(UTC).isoformat(),
        "response": [
            {
                "page": 1,
                "pages": 1,
                "per_page": len(all_records),
                "total": len(all_records),
            },
            all_records,
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{name}.json"

    with output.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2)

    print(f"OK: {name} — {len(all_records)} records")


def main() -> None:
    with requests.Session() as session:
        for name, code in INDICATORS.items():
            collect_indicator(session, name, code)


if __name__ == "__main__":
    main()
