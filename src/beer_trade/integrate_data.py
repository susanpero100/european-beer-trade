from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"


def integrate_data(
    beer: pd.DataFrame,
    worldbank: pd.DataFrame,
) -> pd.DataFrame:
    """Integrate Eurostat trade data with World Bank indicators."""

    if beer.duplicated(["country", "year", "partner", "flow"]).any():
        raise ValueError("Duplicate Eurostat business keys")

    if worldbank.duplicated(["country", "year"]).any():
        raise ValueError("Duplicate World Bank business keys")

    merged = beer.merge(
        worldbank,
        on=["country", "year"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    original_rows = len(beer)
    final_rows = len(merged)

    matched = merged["_merge"].eq("both").sum()
    match_rate = matched / original_rows * 100

    print("Eurostat rows:", original_rows)
    print("World Bank rows:", len(worldbank))
    print("Integrated rows:", final_rows)
    print(f"Match rate: {match_rate:.2f}%")
    print("Unmatched rows:", original_rows - matched)

    if final_rows != original_rows:
        raise ValueError("Unexpected row multiplication or loss")

    if match_rate < 100:
        raise ValueError("Unmatched country-year records found")

    merged = merged.drop(columns="_merge")

    return merged


def main() -> None:
    beer = pd.read_csv(PROCESSED / "beer_trade_clean.csv")
    worldbank = pd.read_csv(PROCESSED / "worldbank_clean.csv")

    final = integrate_data(beer, worldbank)

    output = PROCESSED / "beer_trade_integrated.csv"
    final.to_csv(output, index=False)

    print("\nFinal dataset saved to:", output)
    print(final.head().to_string(index=False))


if __name__ == "__main__":
    main()
