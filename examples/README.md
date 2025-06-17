The `examples/` directory contains small scripts that demonstrate how to use the library programmatically. They are optional and not required for normal operation.

`fractal_example.py` generates a small fractal curve and prints the resulting vertices. This illustrates the `generate_fractal_geometry` helper.

`repair_mesh.py` creates a deliberately broken box mesh and repairs it using `repair_until_watertight`, showing the watertight status of the repaired mesh.

Run an example with `python` from the project root, for example:

```bash
python examples/fractal_example.py
python examples/repair_mesh.py
```
