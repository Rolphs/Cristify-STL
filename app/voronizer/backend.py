"""Compute backend selection for the voronizer pipeline.

The voronizer was originally written with numba CUDA kernels.  On machines
without an NVIDIA GPU (e.g. Apple Silicon) the pipeline transparently falls
back to NumPy/SciPy implementations in :mod:`app.voronizer.cpu_ops`.

Set the environment variable ``CRISTIFY_FORCE_CPU=1`` to force the CPU
backend even when CUDA is available (useful for testing).
"""

import os

_cuda_available = None


def cuda_available() -> bool:
    """Return ``True`` when a usable CUDA GPU is present."""
    global _cuda_available
    if os.environ.get("CRISTIFY_FORCE_CPU"):
        return False
    if _cuda_available is None:
        try:
            from numba import cuda
            _cuda_available = bool(cuda.is_available())
        except Exception:
            _cuda_available = False
    return _cuda_available
