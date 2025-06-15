# Cristify STL

This repository provides utilities for experimenting with STL mesh processing.  The
primary functionality lives inside the `app` package which exposes a simple
command–line interface and an optional GUI built with DearPyGui.

## Project Layout

```
app/        # package with CLI, core utilities, GUI and voronizer modules
assets/     # bundled resource files
data/       # small data assets
scripts/    # standalone demo and optimization scripts
tests/      # pytest suite
```

The files in `scripts/` are experimental helpers and examples.  They are not
required for running the library or tests but are kept for reference.

## Usage

Run the command–line interface:

```bash
python -m app.cli cristify --input INPUT.stl --output OUTPUT.stl
```

Launch the basic GUI:

```bash
python -m app.gui.main_gui
```

## Development

Install dependencies and run the test suite with:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
