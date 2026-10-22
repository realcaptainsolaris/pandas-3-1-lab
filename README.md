# pandas 3.1 `read_csv()` Benchmark

This repository contains the code used for my pandas 3.1 CSV benchmark.

The goal is to compare `pd.read_csv()` performance between pandas 3.0.6 and pandas 3.1.0 using two synthetic 20-million-row datasets.

The benchmarks measure:

- Runtime
- Throughput in rows per second
- Peak process memory
- pandas 3.1 with one thread
- pandas 3.1 with its default parallel CSV reader

## Requirements

You need:

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Linux for the included peak-memory measurement via `resource.getrusage()`

Check that `uv` is installed:

```bash
uv --version
```

## Clone the repository

```bash
git clone git@github.com:realcaptainsolaris/pandas-3-1-lab.git
cd pandas-3-1-lab
```

## Generate the benchmark data

The CSV files are not included in the repository because they are several gigabytes in size.

Generate them locally instead.

### Mixed-type dataset

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

## Run the mixed-type CSV benchmark

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

Run all three sequentially:

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

Run all three sequentially:

```bash
uv run --with pandas==3.0.6 benchmark_numeric.py && \
uv run --with pandas==3.1.0 benchmark_numeric.py --threads 1 && \
uv run --with pandas==3.1.0 benchmark_numeric.py
```

## Benchmark methodology

Each configuration is executed five times.

Every benchmark iteration runs in a fresh Python process. This prevents peak-memory measurements from one iteration carrying over into the next.

The reported results use the median of the five runs.

The benchmark prints the pandas version, Python version, CPU count, file size, and threading configuration so the environment can be verified directly from the output.

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

## Important benchmark caveats

These benchmarks are intended to compare pandas 3.0.6 and pandas 3.1.0 on the same files and machine.

They are not intended to represent every possible CSV workload.

### Operating-system file cache

The same CSV files are read repeatedly during the benchmark.

Later runs may therefore benefit from the operating system's file cache.

The reported numbers should primarily be interpreted as parser and conversion performance rather than cold-storage throughput.

If you want to measure cold-cache performance, you need a separate methodology that explicitly controls the operating system's page cache.

### Peak memory

Peak memory is measured using:

```python
resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
```

On Linux, this reports the maximum resident set size of the complete Python process.

It should therefore be interpreted as peak process memory during the benchmark, not as the memory footprint of the resulting DataFrame alone.

### Threading

The single-threaded pandas 3.1 tests use:

```python
with pd.option_context("mode.max_threads", 1):
    df = pd.read_csv(...)
```

This limits the pandas CSV reader according to the pandas threading configuration.

It should not be interpreted as forcing every library used by the Python process to use exactly one operating-system thread.

### Synthetic data

Both datasets are synthetic.

The mixed-type dataset is designed to exercise several common CSV column types, while the numeric dataset isolates a workload dominated by numeric parsing.

Real-world results will depend on factors such as:

- Column types
- CSV structure
- CPU performance
- Storage performance
- Memory bandwidth
- Available RAM
- Operating system
- Python and dependency versions

## My results

The measurements below were collected with Python 3.14.7 on a machine exposing 16 logical CPUs.

The two datasets should not be compared directly with each other.

Each table compares pandas 3.0.6 and pandas 3.1.0 using exactly the same CSV file.

### Mixed-type CSV

File size: approximately 1.1 GB  
Rows: 20,000,000

| Configuration | Runtime | Throughput | Peak process RAM |
| --- | ---: | ---: | ---: |
| pandas 3.0.6 | 14.861 s | 1.35 M rows/s | 3.44 GB |
| pandas 3.1.0, 1 thread | 4.771 s | 4.19 M rows/s | 1.70 GB |
| pandas 3.1.0, default | 4.745 s | 4.21 M rows/s | 1.70 GB |

On this dataset, pandas 3.1 was a little more than 3× faster than pandas 3.0.6.

The single-threaded and default-threaded pandas 3.1 results were almost identical, which suggests that most of the improvement here came from the faster parser and conversion path rather than parallel reading.

### Numeric CSV

File size: approximately 2.05 GB  
Rows: 20,000,000

| Configuration | Runtime | Throughput | Peak process RAM |
| --- | ---: | ---: | ---: |
| pandas 3.0.6 | 12.754 s | 1.57 M rows/s | 2.21 GB |
| pandas 3.1.0, 1 thread | 4.792 s | 4.17 M rows/s | 1.30 GB |
| pandas 3.1.0, default | 0.905 s | 22.09 M rows/s | 4.28 GB |

On this dataset, pandas 3.1 was about 2.7× faster in single-threaded mode.

With the default parallel reader, runtime dropped from 12.754 seconds to 0.905 seconds, which is roughly a 14× speedup.

The trade-off was memory usage: peak process memory increased to approximately 4.28 GB in the parallel run.

## Reproduce the results

Your results will almost certainly differ from mine.

That is expected.

The purpose of this repository is not to claim that every CSV workload becomes 14× faster.

It is to provide a small, reproducible benchmark that makes it easy to compare pandas 3.0.6 and pandas 3.1.0 on your own hardware.

If you run the benchmark, feel free to compare your numbers with the results above.
