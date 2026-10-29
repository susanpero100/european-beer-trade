import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]

    steps = [
        "prepare_eurostat.py",
        "prepare_worldbank.py",
        "integrate_data.py",
        "calculate_kpis.py",
        "create_figures.py",
    ]

    for step in steps:
        script = Path(__file__).resolve().parent / step

        print(f"\nRunning: {step}", flush=True)

        subprocess.run(
            [sys.executable, str(script)],
            cwd=root,
            check=True,
        )

    print("\nPipeline completed successfully!")
