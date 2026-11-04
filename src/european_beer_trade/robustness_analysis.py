"""Sensitivity analysis of EU beer exports to the final year selected."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data/processed/beer_trade_kpis.csv"
OUTPUT = ROOT / "docs/robustness_analysis.md"

BASE_YEAR = 2019
END_YEARS = [2024, 2025]


def main() -> None:
    df = pd.read_csv(INPUT)

    totals = df.groupby("year")["export_kg"].sum()

    shares = df.pivot(
        index="country",
        columns="year",
        values="export_share_pct",
    )

    lines = [
        "# Robustness Analysis",
        "",
        "## Objective",
        "",
        "Test whether the main findings change when the final "
        "year is 2024 rather than 2025.",
        "",
        "Both scenarios use 2019 as the baseline.",
        "",
        "## Aggregate Export Volume",
        "",
        "| Period | Export volume change |",
        "|---|---:|",
    ]

    for end_year in END_YEARS:
        growth = (totals.loc[end_year] / totals.loc[BASE_YEAR] - 1) * 100

        lines.append(f"| 2019–{end_year} | {growth:+.2f}% |")

    lines.extend(
        [
            "",
            "## Export Share Changes",
            "",
            "Changes are measured in percentage points (pp).",
            "",
        ]
    )

    for end_year in END_YEARS:
        changes = (shares[end_year] - shares[BASE_YEAR]).sort_values(ascending=False)

        lines.extend(
            [
                f"### 2019–{end_year}",
                "",
                "**Top five share gainers**",
                "",
                "| Country | Change (pp) |",
                "|---|---:|",
            ]
        )

        for country, value in changes.head(5).items():
            lines.append(f"| {country} | {value:+.2f} |")

        lines.extend(
            [
                "",
                "**Top five share losers**",
                "",
                "| Country | Change (pp) |",
                "|---|---:|",
            ]
        )

        for country, value in changes.tail(5).sort_values().items():
            lines.append(f"| {country} | {value:+.2f} |")

        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- Aggregate reported exports decline under both endpoints.",
            "- Ireland, Czechia and Spain gain export share in both scenarios.",
            "- The Netherlands loses export share in both scenarios.",
            "- The magnitude and ranking of changes depend on the final year.",
            "",
            "## Limitations",
            "",
            "- This is endpoint sensitivity, not a statistical uncertainty test.",
            "- Recent official trade observations may be revised.",
            "- Export shares measure relative positions, not profitability.",
            "- Results are descriptive and do not establish causality.",
            "",
            "**Source:** Eurostat and World Bank, processed through "
            "the project's reproducible Python pipeline.",
            "",
        ]
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Robustness report created: {OUTPUT}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
