from numba import cuda
import numpy as np
import math


@cuda.jit
def smoothKernel(d_u, d_v, buffer):
    """Average each voxel with its neighbors ignoring ``buffer`` layers."""
    i, j, k = cuda.grid(3)
    count = 0
    dims = d_u.shape
    if i>=dims[0]-buffer or j>=dims[1]-buffer or k>=dims[2]-buffer or i<buffer or j<buffer or k<buffer:
        return
    else:
        d_v[i,j,k]=0
        for index in range(27):
            checkPos = (i+((index//9)%3-1),j+((index//3)%3-1),k+(index%3-1))
            if checkPos[0]<dims[0] and checkPos[1]<dims[1] and checkPos[2]<dims[2] and min(checkPos)>=0:
                d_v[i,j,k]+=d_u[checkPos]
                count+=1
        d_v[i,j,k] = d_v[i,j,k]/count

def smooth(u, iteration=1, buffer=0, tpb=8):
    """Return ``u`` after ``iteration`` smoothing passes.

    Parameters
    ----------
    u : numpy.ndarray
        Input voxel grid.
    iteration : int, optional
        Number of smoothing iterations.
    buffer : int, optional
        Number of boundary layers left unchanged.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Smoothed voxel grid.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    dims = u.shape
    d_u = cuda.to_device(u)
    d_v = cuda.to_device(u)
    gridDims = (dims[0]+TPBX-1)//TPBX, (dims[1]+TPBY-1)//TPBY, (dims[2]+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    for var in range(iteration):
        smoothKernel[gridDims, blockDims](d_u, d_v,buffer)
        d_u,d_v = d_v,d_u
    return d_u.copy_to_host()

@cuda.jit
def boolKernel(d_u,d_v):
    i,j,k = cuda.grid(3)
    dims = d_u.shape
    if i >= dims[0] or j >= dims[1] or k >= dims[2]:
        return
    d_u[i,j,k] = min(d_u[i,j,k],d_v[i,j,k])
    
def union(u, v, tpb=8):
    """Return the voxel-wise union of ``u`` and ``v``.

    Parameters
    ----------
    u, v : numpy.ndarray
        Input voxel models.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Combined voxel model.
    """
    d_u = cuda.to_device(u)
    d_v = cuda.to_device(v)
    dims = u.shape
    gridSize = [(dims[0]+tpb-1)//tpb, (dims[1]+tpb-1)//tpb, (dims[2]+tpb-1)//tpb]
    blockSize = [tpb, tpb, tpb]
    boolKernel[gridSize, blockSize](d_u, d_v)
    return d_u.copy_to_host()

def intersection(u, v, tpb=8):
    """Return the intersection of ``u`` and ``v``.

    Parameters
    ----------
    u, v : numpy.ndarray
        Input voxel models.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Voxel model containing only overlapping cells.
    """
    d_u = cuda.to_device(-1 * u)
    d_v = cuda.to_device(-1 * v)
    dims = u.shape
    gridSize = [(dims[0] + tpb - 1) // tpb, (dims[1] + tpb - 1) // tpb, (dims[2] + tpb - 1) // tpb]
    blockSize = [tpb, tpb, tpb]
    boolKernel[gridSize, blockSize](d_u, d_v)
    return -1 * d_u.copy_to_host()

def subtract(u, v, tpb=8):
    """Subtract ``u`` from ``v``.

    Parameters
    ----------
    u, v : numpy.ndarray
        ``u`` is the cutting tool, ``v`` the base model.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Resulting voxel grid.
    """
    d_u = cuda.to_device(u)
    d_v = cuda.to_device(-1 * v)
    dims = u.shape
    gridSize = [(dims[0] + tpb - 1) // tpb, (dims[1] + tpb - 1) // tpb, (dims[2] + tpb - 1) // tpb]
    blockSize = [tpb, tpb, tpb]
    boolKernel[gridSize, blockSize](d_u, d_v)
    return -1 * d_u.copy_to_host()

@cuda.jit
def projectionKernel(d_u,X):
    j,k = cuda.grid(2)
    m,n,p = d_u.shape
    if j < n and k < p:
        if d_u[X+1,j,k]<=0:
            d_u[X,j,k]=-1    

def projection(u, tpb=8):
    """Project ``u`` downwards along the X axis until contact.

    Parameters
    ----------
    u : numpy.ndarray
        Voxel model to project.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Projected voxel model.
    """
    TPBY, TPBZ = tpb, tpb
    m, n, p = u.shape
    minX = -1
    i = 0
    while minX<0:
        if np.amin(u[i,:,:])<0:
            minX = i
        else:
            i += 1
    X = m-1
    d_u = cuda.to_device(u)
    gridDims = (n + TPBY - 1) // TPBY, (p + TPBZ - 1) // TPBZ
    blockDims = TPBY, TPBZ
    while X>minX:
        X -= 1
        projectionKernel[gridDims, blockDims](d_u,X)
    return d_u.copy_to_host()

@cuda.jit
def translateKernel(d_u,d_v,x,y,z):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i >= m or j >= n or k >= p:
        return
    d_v[i,j,k] = d_u[(i-x)%m,(j-y)%n,(k-z)%p]
    
def translate(u, x, y, z, tpb=8):
    """Translate ``u`` by integer offsets ``x``, ``y``, ``z``.

    Parameters
    ----------
    u : numpy.ndarray
        Voxel grid to translate.
    x, y, z : int
        Translation in voxels.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Translated voxel grid.
    """
    d_u = cuda.to_device(u)
    d_v = cuda.device_array(shape=u.shape, dtype=np.float32)
    dims = u.shape
    gridSize = [(dims[0] + tpb - 1) // tpb, (dims[1] + tpb - 1) // tpb, (dims[2] + tpb - 1) // tpb]
    blockSize = [tpb, tpb, tpb]
    translateKernel[gridSize, blockSize](d_u, d_v, x, y, z)
    return d_v.copy_to_host()

def thicken(u, weight):
    """Offset a signed distance field by ``weight`` voxels."""
    return u - np.ones(u.shape) * weight
    
def shell(uSDF, sT, tpb=8):
    """Return a shell of ``uSDF`` with thickness ``sT``."""
    return intersection(uSDF, -uSDF - np.ones(uSDF.shape) * sT, tpb)

@cuda.jit
def condenseKernel(d_u,d_uCondensed,buffer,minX,minY,minZ):
    i,j,k = cuda.grid(3)
    m,n,p = d_uCondensed.shape
    if i < m and j < n and k < p:
        d_uCondensed[i,j,k] = d_u[i+minX-buffer,j+minY-buffer,k+minZ-buffer]
    
def condense(u, buffer, tpb=8):
    """Crop empty space around ``u`` leaving ``buffer`` voxels.

    Parameters
    ----------
    u : numpy.ndarray
        Input voxel grid.
    buffer : int
        Number of empty layers to retain around geometry.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Condensed voxel grid.
    """
    m, n, p = u.shape
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    minX, maxX, minY, maxY, minZ, maxZ = -1,-1,-1,-1,-1,-1
    i, j, k = 0, 0, 0
    while minX<0:
        if np.amin(u[i,:,:])<0:     minX = i
        else:                       i += 1
    while minY<0:
        if np.amin(u[:,j,:])<0:     minY = j
        else:                       j += 1
    while minZ<0:
        if np.amin(u[:,:,k])<0:     minZ = k
        else:                       k += 1
    i, j, k = 1, 1, 1
    while maxX<0:
        if np.amin(u[m-i,:,:])<0:   maxX = m-i
        else:                       i += 1
    while maxY<0:
        if np.amin(u[:,n-j,:])<0:   maxY = n-j
        else:                       j += 1
    while maxZ<0:
        if np.amin(u[:,:,p-k])<0:   maxZ = p-k
        else:                       k += 1
    xSize = (np.ceil((2 * buffer + maxX - minX) / tpb) * tpb).astype(int)
    ySize = (np.ceil((2 * buffer + maxY - minY) / tpb) * tpb).astype(int)
    zSize = (np.ceil((2 * buffer + maxZ - minZ) / tpb) * tpb).astype(int)
    d_u = cuda.to_device(u)
    d_uCondensed = cuda.device_array(shape = [xSize, ySize, zSize], dtype = np.float32)
    gridDims = (xSize + TPBX - 1) // TPBX, (ySize + TPBY - 1) // TPBY, (zSize + TPBZ - 1) // TPBZ
    blockDims = TPBX, TPBY, TPBZ
    condenseKernel[gridDims, blockDims](d_u, d_uCondensed, buffer, minX, minY, minZ)
    return d_uCondensed.copy_to_host()

@cuda.jit
def heartKernel(d_u, d_x, d_y, d_z,cx,cy,cz):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i < m and j < n and k < p:
        x = d_x[i]-cx
        y = d_y[j]-cy
        z = d_z[k]-cz
        d_u[i,j,k] = (x**2+9*(y**2)/4+z**2-1)**3-(x**2)*(z**3)-9*(y**2)*(z**3)/80
        
def heart(x, y, z, cx, cy, cz, tpb=8):
    """Generate a heart shaped SDF over ``x``, ``y`` and ``z`` grids.

    Parameters
    ----------
    x, y, z : numpy.ndarray
        Coordinate vectors.
    cx, cy, cz : float
        Center of the heart.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Signed distance field of the heart.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    m = x.shape[0]
    n = y.shape[0]
    p = z.shape[0]
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_z = cuda.to_device(z)
    d_u = cuda.device_array(shape = [m, n, p], dtype = np.float32)
    gridDims = (m+TPBX-1)//TPBX, (n+TPBY-1)//TPBY, (n+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    heartKernel[gridDims, blockDims](d_u, d_x, d_y, d_z,cx,cy,cz)
    return d_u.copy_to_host()

@cuda.jit
def eggKernel(d_u, d_x, d_y, d_z,cx,cy,cz):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i < m and j < n and k < p:
        x = d_x[i]-cx
        y = d_y[j]-cy
        z = d_z[k]-cz
        d_u[i,j,k] = 9*x**2+16*(y**2+z**2)+2*x*(y**2+z**2)+(y**2+z**2)-144
        
def egg(x, y, z, cx, cy, cz, tpb=8):
    """Generate an egg shaped SDF.

    Parameters
    ----------
    x, y, z : numpy.ndarray
        Coordinate vectors.
    cx, cy, cz : float
        Center of the egg.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Signed distance field of the egg.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    m = x.shape[0]
    n = y.shape[0]
    p = z.shape[0]
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_z = cuda.to_device(z)
    d_u = cuda.device_array(shape = [m, n, p], dtype = np.float32)
    gridDims = (m+TPBX-1)//TPBX, (n+TPBY-1)//TPBY, (n+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    eggKernel[gridDims, blockDims](d_u, d_x, d_y, d_z,cx,cy,cz)
    return d_u.copy_to_host()

@cuda.jit
def rectKernel(d_u, d_x, d_y, d_z, xl, yl, zl, origin):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i < m and j < n and k < p:
        sx = abs(d_x[i]-origin[0]) - xl/2
        sy = abs(d_y[j]-origin[1]) - yl/2
        sz = abs(d_z[k]-origin[2]) - zl/2
        d_u[i,j,k]=max(sx,sy,sz)
        
def rect(x, y, z, xl, yl, zl, origin=(0, 0, 0), tpb=8):
    """Axis-aligned rectangular prism SDF.

    Parameters
    ----------
    x, y, z : numpy.ndarray
        Coordinate vectors.
    xl, yl, zl : float
        Side lengths of the prism.
    origin : tuple, optional
        Center of the prism.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Signed distance field of the prism.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    m = x.shape[0]
    n = y.shape[0]
    p = z.shape[0]
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_z = cuda.to_device(z)
    d_origin = cuda.to_device(origin)
    d_u = cuda.device_array(shape = [m, n, p], dtype = np.float32)
    gridDims = (m+TPBX-1)//TPBX, (n+TPBY-1)//TPBY, (n+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    rectKernel[gridDims, blockDims](d_u, d_x, d_y, d_z, xl, yl, zl, d_origin)
    return d_u.copy_to_host()

@cuda.jit
def sphereKernel(d_u, d_x, d_y, d_z, rad):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i < m and j < n and k < p:
        d_u[i,j, k] = math.sqrt(d_x[i]**2+d_y[j]**2+d_z[k]**2)-rad
        
def sphere(x, y, z, rad, tpb=8):
    """Generate a sphere SDF.

    Parameters
    ----------
    x, y, z : numpy.ndarray
        Coordinate vectors.
    rad : float
        Radius of the sphere.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Signed distance field of the sphere.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    m = x.shape[0]
    n = y.shape[0]
    p = z.shape[0]
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_z = cuda.to_device(z)
    d_u = cuda.device_array(shape = [m, n, p], dtype = np.float32)
    gridDims = (m+TPBX-1)//TPBX, (n+TPBY-1)//TPBY, (n+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    sphereKernel[gridDims, blockDims](d_u, d_x, d_y, d_z, rad)
    return d_u.copy_to_host()

@cuda.jit
def cylinderXKernel(d_u, d_x, d_y, d_z, start, stop, rad):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i < m and j < n and k < p:
        height = (d_x[i]-start)*(d_x[i]-stop)
        width = math.sqrt(d_y[j]**2+d_z[k]**2)-rad
        d_u[i,j,k] = max(height,width)

def cylinderX(x, y, z, start, stop, rad, tpb=8):
    """Generate a cylinder aligned to the X axis.

    Parameters
    ----------
    x, y, z : numpy.ndarray
        Coordinate vectors.
    start, stop : float
        Bounds of the cylinder along X.
    rad : float
        Radius of the cylinder.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Signed distance field of the cylinder.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    m = x.shape[0]
    n = y.shape[0]
    p = z.shape[0]
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_z = cuda.to_device(z)
    d_u = cuda.device_array(shape = [m, n, p], dtype = np.float32)
    gridDims = (m+TPBX-1)//TPBX, (n+TPBY-1)//TPBY, (n+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    cylinderXKernel[gridDims, blockDims](d_u, d_x, d_y, d_z, start, stop, rad)
    return d_u.copy_to_host()

@cuda.jit
def cylinderYKernel(d_u, d_x, d_y, d_z, start, stop, rad):
    i,j,k = cuda.grid(3)
    m,n,p = d_u.shape
    if i < m and j < n and k < p:
        height = (d_y[j]-start)*(d_y[j]-stop)
        width = math.sqrt(d_x[i]**2+d_z[k]**2)-rad
        d_u[i,j,k] = max(height,width)

def cylinderY(x, y, z, start, stop, rad, tpb=8):
    """Generate a cylinder aligned to the Y axis.

    Parameters
    ----------
    x, y, z : numpy.ndarray
        Coordinate vectors.
    start, stop : float
        Bounds of the cylinder along Y.
    rad : float
        Radius of the cylinder.
    tpb : int, optional
        CUDA threads per block.

    Returns
    -------
    numpy.ndarray
        Signed distance field of the cylinder.
    """
    TPBX, TPBY, TPBZ = tpb, tpb, tpb
    m = x.shape[0]
    n = y.shape[0]
    p = z.shape[0]
    d_x = cuda.to_device(x)
    d_y = cuda.to_device(y)
    d_z = cuda.to_device(z)
    d_u = cuda.device_array(shape = [m, n, p], dtype = np.float32)
    gridDims = (m+TPBX-1)//TPBX, (n+TPBY-1)//TPBY, (n+TPBZ-1)//TPBZ
    blockDims = TPBX, TPBY, TPBZ
    cylinderYKernel[gridDims, blockDims](d_u, d_x, d_y, d_z, start, stop, rad)
    return d_u.copy_to_host()
