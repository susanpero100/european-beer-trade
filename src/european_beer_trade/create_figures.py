from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"


def create_figures() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)

    kpis = pd.read_csv(DATA / "beer_trade_kpis.csv")
    trade = pd.read_csv(DATA / "beer_trade_integrated.csv")

    # Figure 1: EU27 export volumes over time
    yearly = kpis.groupby("year")["export_kg"].sum() / 1e9

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(yearly.index.to_list(), yearly.to_list(), marker="o")
    ax.set_title("EU27 Beer Exports, 2019–2025")
    ax.set_xlabel("Year")
    ax.set_ylabel("Billion kg")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "01_export_trend.png", dpi=200)
    plt.close(fig)

    # Figure 2: Export share changes
    shares = kpis.pivot(
        index="country",
        columns="year",
        values="export_share_pct",
    )
    changes = (shares[2025] - shares[2019]).sort_values()

    selected = pd.concat([changes.head(5), changes.tail(5)]).sort_values()

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(selected.index.to_list(), selected.to_list())
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Beer Export Share Changes, 2019–2025")
    ax.set_xlabel("Percentage-point change")
    fig.tight_layout()
    fig.savefig(FIGURES / "02_share_changes.png", dpi=200)
    plt.close(fig)

    # Figure 3: Intra-EU vs Extra-EU export changes
    selected_trade = trade[
        (trade["flow"] == "EXPORT")
        & (trade["country"].isin(["ES", "IE", "CZ"]))
        & (trade["year"].isin([2019, 2025]))
        & (trade["partner"] != "WORLD")
    ].copy()

    pivot = selected_trade.pivot(
        index=["country", "partner"],
        columns="year",
        values="quantity_kg",
    )

    pivot["growth_pct"] = (pivot[2025] / pivot[2019] - 1) * 100

    comparison = pivot["growth_pct"].unstack("partner")

    comparison = comparison.rename(
        columns={
            "INT_EU27_2020": "Intra-EU",
            "EXT_EU27_2020": "Extra-EU",
        }
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    comparison[["Intra-EU", "Extra-EU"]].plot.bar(ax=ax)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Geographic Drivers of Export Growth")
    ax.set_ylabel("Growth 2019–2025 (%)")
    ax.set_xlabel("Country")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Destination")
    fig.tight_layout()
    fig.savefig(FIGURES / "03_geographic_growth.png", dpi=200)
    plt.close(fig)

    # Figure 4: Top 10 exporters per capita in 2025
    per_capita_2025 = (
        kpis[kpis["year"] == 2025][["country", "exports_per_capita_kg"]]
        .sort_values("exports_per_capita_kg", ascending=False)
        .head(10)
        .sort_values("exports_per_capita_kg")
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(
        per_capita_2025["country"].to_list(),
        per_capita_2025["exports_per_capita_kg"].to_list(),
    )
    ax.set_title("Top 10 EU Beer Exporters per Capita, 2025")
    ax.set_xlabel("kg per person")
    ax.set_ylabel("Country")
    ax.grid(axis="x", alpha=0.25)

    for i, value in enumerate(per_capita_2025["exports_per_capita_kg"].to_list()):
        ax.text(value + 1, i, f"{value:.2f}", va="center")

    fig.tight_layout()
    fig.savefig(FIGURES / "04_exports_per_capita_2025.png", dpi=200)
    plt.close(fig)
    # Figure 4: Beer exports per capita in 2025
    per_capita = (
        kpis.loc[kpis["year"] == 2025, ["country", "exports_per_capita_kg"]]
        .dropna()
        .nlargest(10, "exports_per_capita_kg")
        .sort_values("exports_per_capita_kg")
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(
        per_capita["country"].to_list(),
        per_capita["exports_per_capita_kg"].to_list(),
    )
    ax.set_title("Top 10 EU Beer Exporters per Capita, 2025")
    ax.set_xlabel("Beer exports (kg per resident)")
    ax.set_ylabel("Country")
    ax.grid(axis="x", alpha=0.25)

    for i, value in enumerate(per_capita["exports_per_capita_kg"]):
        ax.text(value + 1, i, f"{value:.2f}", va="center")

    fig.tight_layout()
    fig.savefig(FIGURES / "04_exports_per_capita_2025.png", dpi=200)
    plt.close(fig)

    print("Figures created successfully:")
    for path in sorted(FIGURES.glob("*.png")):
        print(path.name)


if __name__ == "__main__":
    create_figures()
