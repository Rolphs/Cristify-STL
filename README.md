# Cristify STL

*A creative mesh transformation toolkit for digital artists.*

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

**Cristify STL** is a visual and geometric transformation tool for STL files, inspired by the work of artist Christo, who wrapped real-world monuments in fabric as acts of aesthetic and symbolic expression. This application is designed specifically for graphic artists who want to transform 3D models for expressive purposes, creating sculptural digital structures that simulate wrapping, curtains, blocks, or altered materialities.

## 📄 Purpose

To empower digital artists to explore the sculptural potential of STL models through:

* Vertical geometry projection.
* Wrapped or "falling fabric" style transformations.
* Topological cleaning and mesh fixing.
* Watertight mesh generation.
* Intuitive visual interface.

---

## 🔧 Key Features

### 1. Vertical Cristification

Transform any STL into a wrapped sculpture that projects its vertices downward as if pulled by gravity.

### 2. Blockification with Flat Base

Convert any mesh into a clean solid block, with corrected normals and planar grounding.

### 3. Watertight Mesh Repair

Fix holes and create closed, solid meshes ready for 3D printing or simulation.

### 4. Visual Interface

Includes a graphical interface with 3D previews, file selection, transformation options, and STL management.

### 5. STL File Management

Choose models, apply processes, rename, overwrite, save versions, and maintain a clean creative workflow.

---

## 🛋️ User Stories

### Primary user: Digital Graphic Artist

1. **As an artist**, I want to cristify STL models to apply visual transformations inspired by Christo.
2. **As an artist**, I want to convert an STL into a clean block with correct face orientation.
3. **As an artist**, I want to make my STL models watertight.
4. **As an artist**, I want a graphical interface so I don't need to rely on command-line tools.
5. **As an artist**, I want to manage my STL files within the interface.
6. **As an artist**, I want to preview transformations before committing changes.
7. **As an artist**, I want to see a transformation history per file.
8. **As an artist**, I want to export in other formats (OBJ, GLB, PLY).
9. **As an artist**, I want to combine multiple STLs into one composition.
10. **As an artist**, I want to batch-process STL files with the same transformation.

---

## 🧪 Tech Stack

### Core Language

* Python 3.11+

### Geometry and STL Handling

* `trimesh`: Mesh operations, STL loading/writing.
* `open3d`: Booleans, watertight repairs, advanced viewing.
* `pymeshlab`: Mesh repair and optimization.
* `numpy` + `scipy`: Projections, remeshing, geometric math.

### Graphical Interface

* **Dear PyGui**: Modern GPU-accelerated GUI with 3D viewport and reactive widgets.

### Rendering & Visualization

* `DearPyGui` 3D viewport
* `trimesh.SceneViewer`
* `open3d.visualization`

### File Management

* Python built-in `os`, `shutil`, `pathlib` for file browsing, renaming, saving, and versioning.

### Testing & Distribution

* `pytest` for tests
* `PyInstaller` or `briefcase` for packaging as a native desktop app

---

## 📂 Project Structure

```
Cristify-STL/
  app/
    core/
      cristify.py         # Wrapping and projection logic
      mesh_utils.py        # Watertight repairs and cleanup
      io.py                # File loading, saving, renaming
    gui/
      main_gui.py         # Main GUI application
      viewer.py           # 3D visualizer
    assets/               # UI themes, icons
    data/                 # User STL files                  # User STL files
```

---

## 🌍 Future Vision

* [ ] Blender plugin integration

* [ ] Progressive wrapping animations

* [ ] WebXR and AR export

* [ ] Tablet and stylus support

* [ ] Embedded gallery view with previews

## 🧠 Intelligent Mesh Intervention Strategy

Cristify STL aspires to become an intelligent assistant that intervenes in 3D geometry only when it can meaningfully contribute.
It analyzes mesh structure, projects potential transformations, estimates their impact, and requests human input only when its expected contribution is minimal.
This hybrid architecture blends geometric structure, probabilistic learning, and aesthetic judgment.

---

## 🚀 Getting Started for Developers

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install runtime dependencies
pip install -r requirements.txt
# Install development tools (tests, linters)
pip install -r requirements-dev.txt

# Launch GUI
python app/gui/main_gui.py
```

---

## 🌈 Project Philosophy

Cristify STL is based on the idea that 3D models are not just technical assets but **aesthetic matter**. It embraces the notion that digital art needs its own sensitive materials, and that wrapping, deforming, and projecting models is a valid way to create visual, spatial, and narrative meaning.

---

## 🔗 Contributing

This project is a gift to the world—open, free, and expressive. Contributions are welcome from digital artists, creative developers, visual mathematicians, and geometry poets alike.
