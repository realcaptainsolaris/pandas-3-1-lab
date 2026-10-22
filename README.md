# pandas 3.1 `read_csv()` Benchmark

This repository contains the benchmark code used for my pandas 3.1 CSV performance tests.

The goal is simple: compare `pd.read_csv()` performance between pandas 3.0.6 and pandas 3.1.0 using two 20-million-row datasets.

The benchmarks measure:

- Runtime
- Throughput in rows per second
- Peak RAM usage
- pandas 3.1 with one thread
- pandas 3.1 with its default parallel CSV reader

## Requirements

You need:

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Linux for the included peak-memory measurement using `resource.getrusage()`

Check that `uv` is available:

```bash
uv --version
```

## Clone the repository

```bash
git clone https://github.com/realcaptainsolaris/pandas-3-1-lab
cd pandas-3-1-lab
```

## Generate the benchmark data

The CSV files are intentionally not included in the repository because they are several gigabytes in size.

Generate them locally instead.

### Mixed dataset

This dataset contains integers, floats, strings, categories, and timestamps.

```bash
uv run --with pandas generate_csv.py --rows 20000000
```

This creates:

```text
data/benchmark.csv
```

The generated file is roughly 1.1 GB.

### Numeric dataset

This dataset contains only numeric columns.

```bash
uv run --with pandas generate_numeric_csv.py --rows 20000000
```

This creates:

```text
data/numeric.csv
```

The generated file is roughly 2 GB.

Both generators use a fixed random seed so the generated data is reproducible.

## Run the mixed CSV benchmark

### pandas 3.0.6

```bash
uv run --with pandas==3.0.6 benchmark.py
```

### pandas 3.1.0 with one thread

```bash
uv run --with pandas==3.1.0 benchmark.py --threads 1
```

### pandas 3.1.0 with default threading

```bash
uv run --with pandas==3.1.0 benchmark.py
```

You can also run all three sequentially:

```bash
uv run --with pandas==3.0.6 benchmark.py && \
uv run --with pandas==3.1.0 benchmark.py --threads 1 && \
uv run --with pandas==3.1.0 benchmark.py
```

## Run the numeric CSV benchmark

### pandas 3.0.6

```bash
uv run --with pandas==3.0.6 benchmark_numeric.py
```

### pandas 3.1.0 with one thread

```bash
uv run --with pandas==3.1.0 benchmark_numeric.py --threads 1
```

### pandas 3.1.0 with default threading

```bash
uv run --with pandas==3.1.0 benchmark_numeric.py
```

Or run the complete comparison:

```bash
uv run --with pandas==3.0.6 benchmark_numeric.py && \
uv run --with pandas==3.1.0 benchmark_numeric.py --threads 1 && \
uv run --with pandas==3.1.0 benchmark_numeric.py
```

## Benchmark methodology

Each configuration is executed five times.

Every benchmark iteration runs in a fresh Python process. This prevents peak-memory measurements from one run affecting subsequent runs.

The reported results use the median of the five runs.

The benchmark prints the pandas version used for each test so that the environment can be verified directly from the output.

Example:

```text
========================================================================
pandas numeric read_csv benchmark
========================================================================
pandas version : 3.1.0
Python         : 3.14.7
CPU count      : 16
File           : data/numeric.csv
File size      : 2,055.3 MB
Runs           : 5
Max threads    : pandas default
```

## My results

The benchmarks for the accompanying article were run with Python 3.14.7 on a machine exposing 16 logical CPUs.

### Mixed CSV

| Configuration | Runtime | Throughput | Peak RAM |
| --- | ---: | ---: | ---: |
| pandas 3.0.6 | 14.861 s | 1.35 M rows/s | 3.44 GB |
| pandas 3.1.0, 1 thread | 4.771 s | 4.19 M rows/s | 1.70 GB |
| pandas 3.1.0, default | 4.745 s | 4.21 M rows/s | 1.70 GB |

### Numeric CSV

| Configuration | Runtime | Throughput | Peak RAM |
| --- | ---: | ---: | ---: |
| pandas 3.0.6 | 12.754 s | 1.57 M rows/s | 2.21 GB |
| pandas 3.1.0, 1 thread | 4.792 s | 4.17 M rows/s | 1.30 GB |
| pandas 3.1.0, default | 0.905 s | 22.09 M rows/s | 4.28 GB |

Your results will depend on CPU performance, storage speed, available memory, operating system, and the exact Python environment.

That is part of the point of this repository: run the benchmark on your own hardware and compare.
