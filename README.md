# Cristify STL

This repository provides utilities for experimenting with STL mesh processing.  The
primary functionality lives inside the `app` package which exposes a simple
command–line interface and an optional GUI built with DearPyGui.

## Project Layout

```
app/        # package with CLI, core utilities, GUI and voronizer modules
assets/     # bundled resource files
data/       # small data assets
examples/   # simple usage examples
tests/      # pytest suite
```

The examples in `examples/` showcase typical usage and are optional. They are not required for running the library or tests but are kept for reference.

## Mesh Operations

This project bundles several utilities for modifying STL meshes:

### Repair

Remove duplicate vertices and faces and optionally fill simple holes to
produce a clean, watertight mesh.

### Analyze

Inspect a mesh and return heuristic metrics such as the number of isolated
edges, the ratio of flat faces and a simple intervention score.

### Gaudify

Iteratively transform steep overhangs into gothic-like arches to aid 3D
printing.

### Wrap

Offset every vertex along its normal by a configurable thickness, effectively
wrapping the surface.

### Simplify

Reduce the number of faces using quadric decimation while preserving the mesh
shape as much as possible.

### Texturize

Procedural tools to add fractal noise, smooth the surface and apply a simple
gravitational attraction between neighbouring vertices.

### Gravity

Additional utilities implementing a gravity–tension model for more exaggerated
deformations.

## Usage

### Command line

Invoke the CLI with the desired subcommand.  Each command accepts `--help`
for full details.

```bash
# Cristify an STL file
python -m app.cli cristify --input INPUT.stl --output OUTPUT.stl

# Voronize a model
python -m app.cli voronize --file-name model.stl --model

# Repair a mesh
python -m app.cli repair --input INPUT.stl --output fixed.stl

# Analyze metrics
python -m app.cli analyze --input INPUT.stl

# Gaudify to reduce overhangs
python -m app.cli gaudify --input INPUT.stl --output gaudi.stl --angle 45

# Wrap a mesh with a thin shell
python -m app.cli wrap --input INPUT.stl --output wrapped.stl --thickness 0.1

# Simplify geometry
python -m app.cli simplify --input INPUT.stl --output slim.stl --reduction 0.5
```

### GUI

Launch the graphical interface:

```bash
python -m app.gui.main_gui
```

The window lets you load an STL, apply Cristify and Voronize operations, repair
or analyze the mesh and apply transformations such as Gaudify, Simplify, Wrap or
Texturize via a drop-down selector.  Results can be previewed and saved from the
same interface.

## Development

Install dependencies and run the test suite with:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```
