from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate country-year beer trade indicators."""

    world = df[df["partner"] == "WORLD"].copy()

    if world.duplicated(["country", "year", "flow"]).any():
        raise ValueError("Duplicate WORLD trade records")

    quantities = world.pivot(
        index=["country", "year"],
        columns="flow",
        values="quantity_kg",
    ).rename(
        columns={
            "EXPORT": "export_kg",
            "IMPORT": "import_kg",
        }
    )

    values = world.pivot(
        index=["country", "year"],
        columns="flow",
        values="value_eur",
    ).rename(
        columns={
            "EXPORT": "export_eur",
            "IMPORT": "import_eur",
        }
    )

    economic = world[
        ["country", "year", "population", "gdp_per_capita_usd"]
    ].drop_duplicates(["country", "year"])

    result = quantities.join(values).reset_index()

    result = result.merge(
        economic,
        on=["country", "year"],
        how="left",
        validate="one_to_one",
    )

    result["trade_balance_kg"] = result["export_kg"] - result["import_kg"]

    result["trade_balance_eur"] = result["export_eur"] - result["import_eur"]

    result["exports_per_capita_kg"] = result["export_kg"] / result["population"]

    result["export_unit_value_eur_per_kg"] = result["export_eur"] / result[
        "export_kg"
    ].replace(0, float("nan"))

    result = result.sort_values(["country", "year"]).reset_index(drop=True)

    result["export_growth_pct"] = (
        result.groupby("country")["export_kg"].pct_change() * 100
    )

    yearly_totals = result.groupby("year")["export_kg"].transform("sum")

    result["export_share_pct"] = result["export_kg"] / yearly_totals * 100

    if result.duplicated(["country", "year"]).any():
        raise ValueError("Duplicate country-year rows")

    return result


def main() -> None:
    df = pd.read_csv(PROCESSED / "beer_trade_integrated.csv")

    result = calculate_kpis(df)

    output = PROCESSED / "beer_trade_kpis.csv"
    result.to_csv(output, index=False)

    print("Rows:", len(result))
    print("Countries:", result["country"].nunique())
    print("Years:", result["year"].nunique())
    print("Missing growth values:", result["export_growth_pct"].isna().sum())
    print("Saved to:", output)

    print("\nTop 10 exporting countries in 2025:")

    top = result[result["year"] == 2025].nlargest(10, "export_kg")

    print(
        top[
            [
                "country",
                "export_kg",
                "export_share_pct",
                "export_growth_pct",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
