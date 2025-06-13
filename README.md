# Generalised Fuzzy Cognitive Maps

This repository contains a Python implementation of **Generalised Fuzzy Cognitive Maps (GFCMs)**.

## Features

- Reads an *n×n* fuzzy weight matrix **W** and a *1×n* fuzzy input vector **I** from CSV or XLSX files.
- Executes a fuzzy inference pipeline:
  1. Fuzzy interval multiplication (min/mid/max aggregation).
  2. Hyperbolic tangent (`tanh(0.5·x)`) scaling.
  3. Defuzzification via centre-of-gravity (COG).
- Runs for a user-defined number of iterations.
- Prints the final fuzzy intervals and crisp centroids (labelled).
- 3D visualisation of fuzzy triangles and centroids for each concept.

## Installation

1. Clone the repository:  
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```
2. Create and activate a virtual environment (optional):  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:  
   ```bash
   pip install numpy pandas matplotlib openpyxl
   ```

## Usage

```bash
python /mnt/data/fuzzy_pipeline.py path/to/weights.csv path/to/input.csv --iterations 50
```

- **weights.csv**: CSV/XLSX with an *n×n* matrix; cells are fuzzy triples like `"[0.1, 0.5, 0.9]"`.
- **input.csv**: CSV/XLSX with a single row of *n* fuzzy triples.

Example files are provided in the `examples/` directory.

## Output

- Prints labelled final fuzzy intervals and centroids to the console.
- Generates a 3D plot for each concept, showing how the fuzzy interval evolves and its centroid.

## Licence

MIT License

