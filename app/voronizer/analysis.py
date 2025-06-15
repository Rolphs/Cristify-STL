from numba import cuda


@cuda.reduce
def sum_reduce(a, b):
    return a + b

def findVol(u, scale, MAT_DENSITY, name, tpb=8):
    #u = input model
    #scale = [X,Y,Z] size of each voxel, mm
    #MAT_DENSITY = density (g/mm^3) of the print material
    #name = name of the input model
    cellVol = scale[0]*scale[1]*scale[2]
    d_u = cuda.to_device(u)
    dims = u.shape
    gridSize = [
        (dims[0] + tpb - 1) // tpb,
        (dims[1] + tpb - 1) // tpb,
        (dims[2] + tpb - 1) // tpb,
    ]
    blockSize = [tpb, tpb, tpb]
    findVolKernel[gridSize, blockSize](d_u)
    u = d_u.copy_to_host()
    count = sum_reduce(cuda.to_device(u.flatten()))
    vol = cellVol*count
    print(name+" Volume = "+str(round(vol,2))+" mm^3")
    print(name+" Mass = "+str(round(MAT_DENSITY*vol/1000,2))+" g")
    return vol

@cuda.jit
def findVolKernel(d_u):
    i,j,k = cuda.grid(3)
    dims = d_u.shape
    if i >= dims[0] or j >= dims[1] or k >= dims[2]:
        return
    if d_u[i,j,k]>0:
        d_u[i,j,k]=0
    else:
        d_u[i,j,k]=1