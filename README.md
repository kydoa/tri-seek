# tri-seek

[![Language](https://img.shields.io/badge/Language-Python-3776AB)](Trabalho1.py)
[![OpenGL](https://img.shields.io/badge/Graphics-OpenGL%2FGLUT-5586A4)](Visualizacao.py)
[![Course](https://img.shields.io/badge/Course-Computer%20Graphics-8A2BE2)]()
[![Status](https://img.shields.io/badge/Status-Completed-brightgreen)]()

An interactive Python/OpenGL program that finds every triangle containing a point moved by the user, speeding up the search with a uniform grid and bounding-box envelopes.

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Why This Project Is Useful](#why-this-project-is-useful)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Where To Get Help](#where-to-get-help)
- [Maintainers and Contributions](#maintainers-and-contributions)

## What This Project Does

`tri-seek` is a small Python program that allows you to:

- Generate N random triangles from a seed, or load them from a text file.
- Move a point with the mouse (click, drag or follow-cursor mode) or the arrow keys, and see which triangles contain it.
- Combine up to three query stages: uniform-grid subdivision, AABB envelope test and the detailed orientation test.
- Switch between the four required configurations at run time and compare results against the brute-force test.
- Visualize each stage with distinct colors: grid, the point's cell, envelopes, grid candidates, envelope-approved triangles and the triangles that contain the point.
- See per-query counters (total triangles, grid candidates, envelope approvals, detailed tests, hits, time in ms).
- Run a benchmark over several scenarios without OpenGL and export the results to CSV.

Query configurations:

| Key | Configuration |
|-----|---------------|
| `1` | Detailed test on all triangles (reference) |
| `2` | Envelope + detailed test |
| `3` | Grid + detailed test |
| `4` | Grid + envelope + detailed test |

A point exactly on an edge or vertex counts as inside the triangle (numeric tolerance `EPS = 1e-9`). The grid and envelopes store only triangle indices, never copies of the geometry, and are built when the scenario is created or loaded.

## Why This Project Is Useful

- Demonstrates spatial subdivision and bounding volumes in a practical 2D problem.
- Shows when an acceleration structure pays off, and when its cost is not worth it.
- Keeps geometry, acceleration structures, query algorithm and rendering in separate modules.

Main benchmark results (N = 10,000 triangles, 16×8 grid, uniform points): the query time dropped from 20.5 ms (brute force) to 0.46 ms with small triangles (44× faster) and from 23.8 ms to 1.5 ms with medium triangles (16×). All four configurations returned exactly the brute-force result in the 288 benchmark rows (0 divergences).

## Getting Started

### Prerequisites

- Python 3.
- PyOpenGL and GLUT (only for the interactive program; the benchmark runs without OpenGL):

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

### Run

From the repository root run:

```bash
python Trabalho1.py --n 2000 --seed 42 --tamanho 1.0 --grade 32
```

What this does:

1. Generates 2,000 random triangles with seed 42 and average size 1.0.
2. Builds a uniform grid 32 cells wide (the height follows the aspect ratio, so cells are roughly square).
3. Opens the interactive window. Press `h` to list the keys.

## Usage Examples

Load a scenario from a file:

```bash
python Trabalho1.py --arquivo cenario.txt
```

Each line has 6 coordinates and an optional color index: `x1 y1 x2 y2 x3 y3 [cor]`. Empty lines and lines starting with `#` are ignored. Press `s` in the program to save the current scenario in this format.

Interactive program options:

| Option | Description | Default |
|--------|-------------|---------|
| `--n` | Number of triangles | 500 |
| `--seed` | Random seed (printed to the console when drawn at random) | random |
| `--tamanho` | Average triangle size | 1.5 |
| `--grade` | Grid cells in x | 16 |
| `--arquivo` | Load triangles from a file | none |

Keys in the program:

| Key | Action |
|-----|--------|
| `1`..`4` | Select configuration |
| `g` / `e` | Turn the grid / envelope stage on or off |
| `d` `z` `b` `c` `v` `f` | Show grid, point's cell, envelopes, grid candidates, envelope-approved, triangles containing the point |
| Arrows (SHIFT = 10× step), click/drag, `m` | Move the point (`m` = follow the mouse) |
| `[` `]` | Decrease / increase grid resolution |
| `+` `-` | Double / halve N |
| `n` | New scenario (new seed) |
| `k` | Toggle verification against brute force |
| `s` | Save scenario |
| `B` | Benchmark of the 4 configurations |
| `h`, `q`/ESC | Help, quit |

Color legend: the point's cell is yellow, grid candidates orange, envelope-approved triangles blue and triangles containing the point green.

Run the benchmark (no OpenGL needed). This command reproduces the results above:

```bash
python Benchmark.py --n 100 1000 10000 --tamanho 0.5 2 --seeds 1 2 --grade 4 16 64 --pontos uniforme dentro --consultas 200 --csv resultados.csv
```

| Option | Description | Default |
|--------|-------------|---------|
| `--n` | Triangle counts | 100 1000 10000 |
| `--tamanho` | Average sizes | 0.5 2.0 |
| `--seeds` | Scenario seeds | 1 2 |
| `--grade` | Grid widths in cells | 4 16 64 |
| `--pontos` | Query positions: `uniforme` (whole area) or `dentro` (inside random triangles) | uniforme dentro |
| `--consultas` | Queries per scenario | 200 |
| `--csv` | Output file | `resultados.csv` |

All configurations run on the same scenarios and the same query positions (fixed seed 999). Counters are identical on any machine; only the time columns depend on the hardware.

## Project Structure

```text
.
├── README.md
├── Ponto.py, ListaDeCoresRGB.py   # Base code (point and color table)
├── Triangulo.py                   # Vertices, AABB envelope and detailed test (no OpenGL)
├── Cenario.py                     # Seeded random generation, load/save, size statistics
├── Aceleracao.py                  # Uniform grid that stores only triangle indices
├── Consulta.py                    # Query: grid -> envelope -> detailed, counters and time
├── Visualizacao.py                # All the OpenGL drawing code
├── Trabalho1.py                   # Interactive program (events, keyboard, mouse, on-screen legend)
└── Benchmark.py                   # Compares the 4 configurations and writes resultados.csv
```

## Where To Get Help

- Inspect [Trabalho1.py](Trabalho1.py) for the interactive entry point; press `h` in the program for the key list.
- For the query pipeline see [Consulta.py](Consulta.py), and for the grid see [Aceleracao.py](Aceleracao.py).

## Maintainers and Contributions

Maintainer:

- [@kydoa](https://github.com/kydoa)
