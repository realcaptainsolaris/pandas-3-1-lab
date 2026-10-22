from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd


def run_worker(path: Path, max_threads: int | None) -> None:
    """Run exactly one numeric CSV benchmark."""

    gc.collect()

    start = time.perf_counter()

    if max_threads is None:
        df = pd.read_csv(
            path,
            engine="c",
        )
    else:
        with pd.option_context("mode.max_threads", max_threads):
            df = pd.read_csv(
                path,
                engine="c",
            )

    duration = time.perf_counter() - start

    rows = len(df)
    rows_per_second = rows / duration

    # Linux reports ru_maxrss in KiB.
    peak_ram_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

    result = {
        "duration": duration,
        "rows": rows,
        "rows_per_second": rows_per_second,
        "peak_ram_mb": peak_ram_mb,
    }

    print(json.dumps(result))


def run_benchmark(
    path: Path,
    runs: int,
    max_threads: int | None,
) -> None:
    """Run every benchmark iteration in a separate process."""

    print("=" * 72)
    print("pandas numeric read_csv benchmark")
    print("=" * 72)
    print(f"pandas version : {pd.__version__}")
    print(f"Python         : {platform.python_version()}")
    print(f"CPU count      : {os.cpu_count()}")
    print(f"File           : {path}")
    print(f"File size      : {path.stat().st_size / 1024**2:,.1f} MB")
    print(f"Runs           : {runs}")

    if max_threads is None:
        print("Max threads    : pandas default")
    else:
        print(f"Max threads    : {max_threads}")

    print()

    durations = []
    peak_ram_values = []
    throughput_values = []

    for run_number in range(1, runs + 1):
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--file",
            str(path),
        ]

        if max_threads is not None:
            command.extend(
                [
                    "--threads",
                    str(max_threads),
                ]
            )

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        result = json.loads(completed.stdout.strip())

        duration = result["duration"]
        rows = result["rows"]
        rows_per_second = result["rows_per_second"]
        peak_ram_mb = result["peak_ram_mb"]

        durations.append(duration)
        peak_ram_values.append(peak_ram_mb)
        throughput_values.append(rows_per_second)

        print(
            f"Run {run_number}: "
            f"{duration:.3f} s | "
            f"{rows_per_second / 1_000_000:.2f} M rows/s | "
            f"{peak_ram_mb:,.0f} MB peak RAM | "
            f"{rows:,} rows"
        )

    median_duration = statistics.median(durations)
    median_peak_ram = statistics.median(peak_ram_values)
    median_throughput = statistics.median(throughput_values)

    print()
    print("-" * 72)
    print(f"Median runtime   : {median_duration:.3f} s")
    print(f"Median throughput: {median_throughput / 1_000_000:.2f} M rows/s")
    print(f"Median peak RAM  : {median_peak_ram:,.0f} MB")
    print(f"Best runtime     : {min(durations):.3f} s")
    print(f"Worst runtime    : {max(durations):.3f} s")
    print("-" * 72)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        type=Path,
        default=Path("data/numeric.csv"),
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--threads",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--worker",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.file.exists():
        raise FileNotFoundError(args.file)

    if args.worker:
        run_worker(
            path=args.file,
            max_threads=args.threads,
        )
        return

    run_benchmark(
        path=args.file,
        runs=args.runs,
        max_threads=args.threads,
    )


if __name__ == "__main__":
    main()
