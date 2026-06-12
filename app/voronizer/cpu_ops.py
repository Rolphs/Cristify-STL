"""NumPy/SciPy implementations of the voronizer CUDA kernels.

Each function mirrors the semantics of its GPU counterpart in
:mod:`app.voronizer.Frep`, :mod:`app.voronizer.SDF3D`,
:mod:`app.voronizer.pointGen`, :mod:`app.voronizer.voronize`,
:mod:`app.voronizer.voxelize`, :mod:`app.voronizer.analysis` and
:mod:`app.voronizer.visualizeSlice`.  They are used automatically when no
CUDA capable GPU is available (see :mod:`app.voronizer.backend`).
"""

import numpy as np
from scipy import ndimage

_NEIGHBOR_OFFSETS = [
    (dx, dy, dz)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    for dz in (-1, 0, 1)
    if (dx, dy, dz) != (0, 0, 0)
]


def smooth(u, iteration=1, buffer=0):
    """Average each voxel with its 26 neighbors, ``iteration`` times."""
    u = np.array(u, dtype=np.float32)
    kernel = np.ones((3, 3, 3))
    counts = ndimage.convolve(np.ones(u.shape), kernel, mode="constant", cval=0.0)
    for _ in range(iteration):
        v = (ndimage.convolve(u.astype(np.float64), kernel, mode="constant", cval=0.0) / counts).astype(np.float32)
        if buffer > 0:
            inner = (
                slice(buffer, u.shape[0] - buffer),
                slice(buffer, u.shape[1] - buffer),
                slice(buffer, u.shape[2] - buffer),
            )
            out = u.copy()
            out[inner] = v[inner]
            v = out
        u = v
    return u


def union(u, v):
    """Voxel-wise union of two signed fields (element-wise minimum)."""
    return np.minimum(u, v)


def intersection(u, v):
    """Voxel-wise intersection (element-wise maximum)."""
    return np.maximum(u, v)


def subtract(u, v):
    """Subtract ``u`` (cutting tool) from ``v`` (base model)."""
    return np.maximum(-np.asarray(u), v)


def projection(u):
    """Project ``u`` downwards along the X axis until contact."""
    u = np.array(u)
    minX = 0
    while np.amin(u[minX]) >= 0:
        minX += 1
    for X in range(u.shape[0] - 2, minX - 1, -1):
        u[X][u[X + 1] <= 0] = -1
    return u


def translate(u, x, y, z):
    """Translate ``u`` by integer voxel offsets with wraparound."""
    return np.roll(np.asarray(u, dtype=np.float32), (x, y, z), axis=(0, 1, 2))


def condense(u, buffer, tpb=8):
    """Crop empty space around ``u`` leaving ``buffer`` voxels of padding.

    Output dimensions are rounded up to a multiple of ``tpb`` to match the
    GPU implementation.
    """
    u = np.asarray(u)
    neg = np.argwhere(u < 0)
    mins = neg.min(axis=0)
    maxs = neg.max(axis=0)
    sizes = [
        int(np.ceil((2 * buffer + maxs[a] - mins[a]) / tpb) * tpb)
        for a in range(3)
    ]
    fill = np.float32(max(np.max(u), 0.01))
    out = np.full(sizes, fill, dtype=np.float32)
    src_slices = []
    dst_slices = []
    for a in range(3):
        start = mins[a] - buffer
        src_start = max(start, 0)
        dst_start = src_start - start
        length = min(u.shape[a] - src_start, sizes[a] - dst_start)
        src_slices.append(slice(src_start, src_start + length))
        dst_slices.append(slice(dst_start, dst_start + length))
    out[tuple(dst_slices)] = u[tuple(src_slices)]
    return out


def _grids(x, y, z, cx=0.0, cy=0.0, cz=0.0):
    X = (np.asarray(x, dtype=np.float64) - cx)[:, None, None]
    Y = (np.asarray(y, dtype=np.float64) - cy)[None, :, None]
    Z = (np.asarray(z, dtype=np.float64) - cz)[None, None, :]
    return X, Y, Z


def heart(x, y, z, cx, cy, cz):
    """Heart shaped SDF over the given coordinate vectors."""
    X, Y, Z = _grids(x, y, z, cx, cy, cz)
    u = (X**2 + 9 * Y**2 / 4 + Z**2 - 1) ** 3 - X**2 * Z**3 - 9 * Y**2 * Z**3 / 80
    return u.astype(np.float32)


def egg(x, y, z, cx, cy, cz):
    """Egg shaped SDF."""
    X, Y, Z = _grids(x, y, z, cx, cy, cz)
    u = 9 * X**2 + 16 * (Y**2 + Z**2) + 2 * X * (Y**2 + Z**2) + (Y**2 + Z**2) - 144
    return u.astype(np.float32)


def rect(x, y, z, xl, yl, zl, origin=(0, 0, 0)):
    """Axis-aligned rectangular prism SDF."""
    X, Y, Z = _grids(x, y, z, *origin)
    u = np.maximum.reduce([
        np.broadcast_to(np.abs(X) - xl / 2, (len(x), len(y), len(z))),
        np.broadcast_to(np.abs(Y) - yl / 2, (len(x), len(y), len(z))),
        np.broadcast_to(np.abs(Z) - zl / 2, (len(x), len(y), len(z))),
    ])
    return u.astype(np.float32)


def sphere(x, y, z, rad):
    """Sphere SDF centered at the origin."""
    X, Y, Z = _grids(x, y, z)
    return (np.sqrt(X**2 + Y**2 + Z**2) - rad).astype(np.float32)


def cylinderX(x, y, z, start, stop, rad):
    """Cylinder SDF aligned to the X axis."""
    X, Y, Z = _grids(x, y, z)
    height = (X - start) * (X - stop)
    width = np.sqrt(Y**2 + Z**2) - rad
    return np.maximum(height, width).astype(np.float32)


def cylinderY(x, y, z, start, stop, rad):
    """Cylinder SDF aligned to the Y axis."""
    X, Y, Z = _grids(x, y, z)
    height = (Y - start) * (Y - stop)
    width = np.sqrt(X**2 + Z**2) - rad
    return np.maximum(height, width).astype(np.float32)


def toFRep(u):
    """Convert boolean voxels to a simple FRep field."""
    return np.where(np.asarray(u), np.float32(-0.01), np.float32(0.01))


def jumpFlood(u, norm=2.0):
    """Nearest seed coordinates and distance for every voxel.

    Seeds are the voxels of ``u`` that are ``<= 0``.  Returns an array of
    shape ``u.shape + (4,)`` holding ``(x, y, z, dist)`` per voxel, matching
    the GPU jump flooding output.
    """
    u = np.asarray(u)
    dims = u.shape
    seeds = u <= 0
    out = np.full(dims + (4,), 1000.0, dtype=np.float32)
    if not seeds.any():
        return out
    if norm == 2.0:
        dist, idx = ndimage.distance_transform_edt(~seeds, return_indices=True)
        out[..., 0] = idx[0]
        out[..., 1] = idx[1]
        out[..., 2] = idx[2]
        out[..., 3] = dist
        return out
    # Generic Minkowski norms: vectorized jump flooding.
    ii, jj, kk = np.indices(dims, dtype=np.float32)
    out[seeds, 0] = ii[seeds]
    out[seeds, 1] = jj[seeds]
    out[seeds, 2] = kk[seeds]
    out[seeds, 3] = 0.0
    n = int(round(np.log2(max(dims) - 1) + 0.5))
    steps = [2 ** (n - c - 1) for c in range(n)] + [2, 1]
    for step in steps:
        for dx, dy, dz in _NEIGHBOR_OFFSETS:
            cand = np.roll(out, (dx * step, dy * step, dz * step), axis=(0, 1, 2))
            d = (
                np.abs((ii - cand[..., 0]) ** norm)
                + np.abs((jj - cand[..., 1]) ** norm)
                + np.abs((kk - cand[..., 2]) ** norm)
            ) ** (1.0 / norm)
            better = d < out[..., 3]
            out[better, :3] = cand[better, :3]
            out[better, 3] = d[better]
    return out


def SDF3D(u, norm=2.0):
    """Convert a binary volume to a signed distance field."""
    u = np.asarray(u)
    pos = jumpFlood(u, norm)
    neg = jumpFlood(-u, norm)
    dp = pos[..., 3]
    dn = neg[..., 3]
    return np.where(dp > 0, dp, -dn).astype(np.float32)


def simplify(u):
    """Flatten the field to thin -0.01/0/0.01 bands for faster processing."""
    u = np.asarray(u)
    footprint = np.ones((3, 3, 3), dtype=bool)
    footprint[1, 1, 1] = False
    nmax = ndimage.maximum_filter(u, footprint=footprint, mode="nearest")
    nmin = ndimage.minimum_filter(u, footprint=footprint, mode="nearest")
    out = np.where(u <= 0, np.float32(-0.01), np.float32(0.01))
    out[(u <= 0) & (nmax > 0) & (nmin < 0)] = 0.0
    return out.astype(np.float32)


def xHeight(u):
    """Cumulative height of solid voxels along X."""
    v = simplify(u)
    for i in range(v.shape[0] - 2, 0, -1):
        mask = v[i] <= 0
        v[i][mask] = np.minimum(-1.0, v[i + 1][mask] - 1.0)
    return v


def genRandPoints(u, threshold):
    """Random seed points inside ``u`` (zeros mark points, ones elsewhere)."""
    u = np.asarray(u)
    x, y, z = u.shape
    threshold = threshold / max(x, y, z)
    r = np.random.rand(x, y, z)
    v = np.ones(u.shape)
    with np.errstate(divide="ignore"):
        mask = (u < 0) & (r < threshold / np.abs(u))
    v[mask] = 0
    print(str(int(x * y * z - v.sum() + 0.5)) + " Points")
    return v


def wallFinder(points):
    """Mark voxels whose nearest seed differs from a neighbor's as walls."""
    points = np.asarray(points)
    seeds = points[..., :3]
    walls = np.ones(points.shape[:3])
    for offset in _NEIGHBOR_OFFSETS:
        shifted = np.roll(seeds, offset, axis=(0, 1, 2))
        walls[np.any(shifted != seeds, axis=-1)] = -1
    return walls


def findVol(u, scale, MAT_DENSITY, name):
    """Volume (mm^3) and mass of the solid voxels of ``u``."""
    cellVol = scale[0] * scale[1] * scale[2]
    count = np.count_nonzero(np.asarray(u) <= 0)
    vol = cellVol * count
    print(name + " Volume = " + str(round(vol, 2)) + " mm^3")
    print(name + " Mass = " + str(round(MAT_DENSITY * vol / 1000, 2)) + " g")
    return vol


def setColor(u, color, background):
    """RGB image stack for ``u`` (solid voxels get ``color``)."""
    u = np.asarray(u)
    image = np.empty(u.shape + (3,), dtype=np.uint8)
    solid = u < 0
    for i in range(3):
        image[..., i] = np.where(solid, color[i], background[i])
    return image
