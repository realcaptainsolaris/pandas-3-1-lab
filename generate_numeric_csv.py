import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_numeric_csv(
    path: Path,
    rows: int,
    chunk_size: int = 1_000_000,
) -> None:
    rng = np.random.default_rng(42)

    path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating {rows:,} numeric rows")
    print(f"Output: {path}")

    first = True

    for start in range(0, rows, chunk_size):
        size = min(chunk_size, rows - start)

        df = pd.DataFrame(
            {
                "id": np.arange(start, start + size, dtype=np.int64),
                "value_a": rng.random(size),
                "value_b": rng.random(size),
                "value_c": rng.random(size),
                "quantity": rng.integers(
                    1,
                    1000,
                    size=size,
                    dtype=np.int32,
                ),
                "score": rng.normal(
                    100,
                    20,
                    size=size,
                ),
                "ratio": rng.random(size),
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

    print()
    print(f"Done: {size_mb:,.1f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--rows",
        type=int,
        default=20_000_000,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/numeric.csv"),
    )

    args = parser.parse_args()

    generate_numeric_csv(
        path=args.output,
        rows=args.rows,
    )
