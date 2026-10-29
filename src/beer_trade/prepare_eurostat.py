from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "eurostat" / "beer_trade_raw.csv"

OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "beer_trade_clean.csv"

KEY_COLUMNS = [
    "reporter",
    "TIME_PERIOD",
    "partner",
    "FLOW",
]


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform Eurostat observations into an analytical table."""

    required = KEY_COLUMNS + ["indicators", "OBS_VALUE"]

    if df[required].isna().any().any():
        raise ValueError("Missing values in required fields")

    if df.duplicated(KEY_COLUMNS + ["indicators"]).any():
        raise ValueError("Duplicate observations found")

    cleaned = df.pivot(
        index=KEY_COLUMNS,
        columns="indicators",
        values="OBS_VALUE",
    ).reset_index()

    cleaned.columns.name = None

    cleaned = cleaned.rename(
        columns={
            "reporter": "country",
            "TIME_PERIOD": "year",
            "FLOW": "flow",
            "QUANTITY_KG": "quantity_kg",
            "VALUE_EUR": "value_eur",
        }
    )

    cleaned = cleaned.sort_values(["country", "year", "partner", "flow"]).reset_index(
        drop=True
    )

    return cleaned


def main() -> None:
    raw = pd.read_csv(INPUT_FILE)
    cleaned = prepare_data(raw)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_FILE, index=False)

    print("Raw rows:", len(raw))
    print("Clean rows:", len(cleaned))
    print("Countries:", cleaned["country"].nunique())
    print("Years:", cleaned["year"].nunique())
    print("Saved to:", OUTPUT_FILE)
    print(cleaned.head().to_string(index=False))


if __name__ == "__main__":
    main()
