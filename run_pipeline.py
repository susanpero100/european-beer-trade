import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = [
    "prepare_eurostat.py",
    "prepare_worldbank.py",
    "integrate_data.py",
    "calculate_kpis.py",
    "create_figures.py",
]


def main() -> None:
    for step in STEPS:
        script = ROOT / "src" / "beer_trade" / step

        print(f"\nRunning: {step}", flush=True)

        subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            check=True,
        )

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    main()

    