import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "worldbank"
OUTPUT = ROOT / "data" / "processed" / "worldbank_clean.csv"

EU27 = {
    "AUT": "AT",
    "BEL": "BE",
    "BGR": "BG",
    "HRV": "HR",
    "CYP": "CY",
    "CZE": "CZ",
    "DNK": "DK",
    "EST": "EE",
    "FIN": "FI",
    "FRA": "FR",
    "DEU": "DE",
    "GRC": "GR",
    "HUN": "HU",
    "IRL": "IE",
    "ITA": "IT",
    "LVA": "LV",
    "LTU": "LT",
    "LUX": "LU",
    "MLT": "MT",
    "NLD": "NL",
    "POL": "PL",
    "PRT": "PT",
    "ROU": "ROU",
    "SVK": "SK",
    "SVN": "SI",
    "ESP": "ES",
    "SWE": "SE",
}

EU27["ROU"] = "RO"


def load_indicator(filename: str, column: str) -> pd.DataFrame:
    path = RAW_DIR / filename

    with path.open(encoding="utf-8") as file:
        snapshot = json.load(file)

    records = snapshot["response"][1]
    df = pd.DataFrame(records)

    df = df[df["countryiso3code"].isin(EU27)].copy()

    df["country"] = df["countryiso3code"].map(EU27)
    df["year"] = df["date"].astype(int)

    df = df.rename(columns={"value": column})

    result = df[["country", "year", column]].copy()

    if len(result) != 189:
        raise ValueError(f"Expected 189 rows, received {len(result)}")

    if result.duplicated(["country", "year"]).any():
        raise ValueError("Duplicate country-year combinations")

    return result


def main() -> None:
    population = load_indicator("population.json", "population")

    gdp = load_indicator("gdp_per_capita_usd.json", "gdp_per_capita_usd")

    merged = population.merge(
        gdp,
        on=["country", "year"],
        how="outer",
        validate="one_to_one",
        indicator=True,
    )

    if not merged["_merge"].eq("both").all():
        raise ValueError("World Bank indicator mismatch")

    merged = merged.drop(columns="_merge")
    merged = merged.sort_values(["country", "year"]).reset_index(drop=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT, index=False)

    print("Rows:", len(merged))
    print("Countries:", merged["country"].nunique())
    print("Years:", merged["year"].nunique())
    print("Missing population:", merged["population"].isna().sum())
    print(
        "Missing GDP per capita:",
        merged["gdp_per_capita_usd"].isna().sum(),
    )
    print("Saved to:", OUTPUT)
    print(merged.head().to_string(index=False))


if __name__ == "__main__":
    main()
