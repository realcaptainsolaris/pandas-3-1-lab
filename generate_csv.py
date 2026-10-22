import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_csv(path: Path, rows: int, chunk_size: int = 1_000_000) -> None:
    rng = np.random.default_rng(42)

    path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating {rows:,} rows")
    print(f"Output: {path}")

    first = True

    for start in range(0, rows, chunk_size):
        size = min(chunk_size, rows - start)

        df = pd.DataFrame(
            {
                "id": np.arange(start, start + size, dtype=np.int64),
                "quantity": rng.integers(1, 100, size=size, dtype=np.int32),
                "price": rng.uniform(1, 1000, size=size).round(2),
                "discount": rng.uniform(0, 0.30, size=size).round(4),
                "category": rng.choice(
                    ["hardware", "software", "books", "office", "other"],
                    size=size,
                ),
                "region": rng.choice(
                    ["north", "south", "east", "west"],
                    size=size,
                ),
                "timestamp": pd.date_range(
                    "2025-01-01",
                    periods=size,
                    freq="s",
                ).astype(str),
            }
        )

        df.to_csv(
            path,
            mode="w" if first else "a",
            header=first,
            index=False,
        )

        first = False
        print(f"{start + size:,} / {rows:,}")

    size_mb = path.stat().st_size / 1024**2
    print(f"Done: {size_mb:,.1f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=20_000_000)
    parser.add_argument("--output", type=Path, default=Path("data/benchmark.csv"))

    args = parser.parse_args()

    generate_csv(args.output, args.rows)
