import json
from datetime import UTC, datetime
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "worldbank"

INDICATORS = {
    "population": "SP.POP.TOTL",
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
}

API_BASE = "https://api.worldbank.org/v2/country"


def collect_indicator(name: str, code: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    url = f"{API_BASE}/all/indicator/{code}"

    params: dict[str, str | int] = {
        "format": "json",
        "date": "2019:2025",
        "per_page": 20000,
        "page": 1,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list) or len(payload) != 2:
        raise ValueError("Unexpected World Bank response")

    metadata, records = payload

    if int(metadata["pages"]) != 1:
        raise ValueError("Multiple pages detected: pagination required")

    if not records:
        raise ValueError("No World Bank records returned")

    snapshot = {
        "source": "World Bank API",
        "indicator": code,
        "url": response.url,
        "extracted_at": datetime.now(UTC).isoformat(),
        "response": payload,
    }

    output = OUTPUT_DIR / f"{name}.json"

    with output.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2)

    print(f"OK: {name}")
    print(f"Records downloaded: {len(records)}")
    print(f"Saved to: {output}")


def main() -> None:
    for name, code in INDICATORS.items():
        collect_indicator(name, code)


if __name__ == "__main__":
    main()
