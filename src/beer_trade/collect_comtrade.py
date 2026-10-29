import json
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

API_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "comtrade"

COUNTRIES = {
    "France": 251,
    "Germany": 276,
    "Italy": 380,
    "Spain": 724,
    "Netherlands": 528,
    "Belgium": 56,
    "Poland": 616,
    "Czechia": 203,
    "Austria": 40,
    "Denmark": 208,
    "Sweden": 752,
    "Portugal": 620,
}

YEARS = range(2019, 2025)
FLOWS = {"X": "export", "M": "import"}


def collect_data() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    successful = 0
    skipped = 0
    failed = []

    for country, code in COUNTRIES.items():
        for year in YEARS:
            for flow_code, flow_name in FLOWS.items():
                filename = f"{code}_{year}_{flow_name}.json"
                output = RAW_DIR / filename

                if output.exists():
                    print(f"SKIPPED: {country} {year} {flow_name}")
                    skipped += 1
                    continue

                params = {
                    "period": str(year),
                    "reporterCode": str(code),
                    "partnerCode": "0",
                    "cmdCode": "2203",
                    "flowCode": flow_code,
                }

                try:
                    response = session.get(
                        API_URL,
                        params=params,
                        timeout=30,
                    )

                    if response.status_code == 429:
                        raise RuntimeError(
                            "UN Comtrade rate limit reached. "
                            "Collection stopped; rerun later to resume."
                        )

                    response.raise_for_status()
                    payload = response.json()

                    if payload.get("error") or payload.get("count") != 1:
                        raise ValueError(
                            f"Unexpected API response: "
                            f"{payload.get('error')}, "
                            f"count={payload.get('count')}"
                        )

                    record = payload["data"][0]

                    if (
                        int(record["reporterCode"]) != code
                        or int(record["refYear"]) != year
                        or record["flowCode"] != flow_code
                        or record["cmdCode"] != "2203"
                        or record["partnerCode"] != 0
                    ):
                        raise ValueError("Record does not match requested filters")

                    snapshot = {
                        "source": "UN Comtrade",
                        "endpoint": "public preview",
                        "url": response.url,
                        "extracted_at": datetime.now(UTC).isoformat(),
                        "country": country,
                        "response": payload,
                    }

                    with output.open("w", encoding="utf-8") as file:
                        json.dump(snapshot, file, indent=2)

                    successful += 1
                    print(f"OK: {country} {year} {flow_name}")

                except RuntimeError:
                    print("RATE LIMIT: stopping collection safely.")
                    raise

                except (
                    requests.RequestException,
                    ValueError,
                    KeyError,
                    TypeError,
                ) as exc:
                    failed.append(f"{country} {year} {flow_name}: {exc}")
                    print(f"FAILED: {country} {year} {flow_name}: {exc}")

                time.sleep(5)

    print(f"\nSuccessful downloads: {successful}")
    print(f"Previously downloaded: {skipped}")
    print(f"Failed downloads: {len(failed)}")

    if failed:
        for item in failed:
            print(item)
        raise RuntimeError("Collection incomplete")


if __name__ == "__main__":
    collect_data()
