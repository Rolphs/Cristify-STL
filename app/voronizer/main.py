import os #Just used to set up file directory
import time
import numpy as np
from . import Frep as f
from .voronize import voronize
from .SDF3D import SDF3D, xHeight
from .pointGen import genRandPoints, explode
from .meshExport import generateMesh
from .analysis import findVol
from .visualizeSlice import slicePlot, contourPlot, generateImageStack
from .voxelize import voxelize
from .__init__ import PipelineConfig

def main(config: PipelineConfig) -> None:
    start = time.time()
    try:
        os.mkdir(os.path.join(os.path.dirname(__file__), 'Output'))
    except Exception:
        pass
    FILE_NAME = config.FILE_NAME
    PRIMITIVE_TYPE = config.PRIMITIVE_TYPE
    modelImport = False
    scale = [1,1,1]
    if not config.MODEL and not config.SUPPORT:
        print("You need at least the model or the support structure.")
        return
    if FILE_NAME != "":
        shortName = FILE_NAME[:-4]
        modelImport = True
        try:    filepath = os.path.join(os.path.dirname(__file__), 'Input',FILE_NAME)
        except: 
            print("Input file not found.") 
            return
        res = config.RESOLUTION - config.BUFFER * 2
        origShape, objectBox = voxelize(filepath, res, config.BUFFER, config.TPB)
        gridResX, gridResY, gridResZ = origShape.shape
        scale[0] = objectBox[0] / (gridResX - config.BUFFER * 2)
        scale[1] = max(objectBox[1:]) / (gridResY - config.BUFFER * 2)
        scale[2] = scale[1]
    elif PRIMITIVE_TYPE != "":
        shortName = PRIMITIVE_TYPE
        if PRIMITIVE_TYPE == "Heart":
            x0 = np.linspace(-1.5, 1.5, config.RESOLUTION)
            y0, z0 = x0, x0
            origShape = f.heart(x0, y0, z0, 0, 0, 0, config.TPB)
        elif PRIMITIVE_TYPE == "Egg":
            x0 = np.linspace(-5, 5, config.RESOLUTION)
            y0, z0 = x0, x0
            origShape = f.egg(x0, y0, z0, 0, 0, 0, config.TPB)
            #eggknowledgement to Molly Carton for this feature.
        else:
            x0 = np.linspace(-50, 50, config.RESOLUTION)
            y0, z0 = x0, x0
            if PRIMITIVE_TYPE == "Cube":
                origShape = f.rect(x0, y0, z0, 80, 80, 80, tpb=config.TPB)
            elif PRIMITIVE_TYPE == "Silo":
                origShape = f.union(
                    f.sphere(x0, y0, z0, 40, config.TPB),
                    f.cylinderY(x0, y0, z0, -40, 0, 40, config.TPB),
                    config.TPB,
                )
            elif PRIMITIVE_TYPE == "Cylinder":
                origShape = f.cylinderX(x0, y0, z0, -40, 40, 40, config.TPB)
            elif PRIMITIVE_TYPE == "Sphere":
                origShape = f.sphere(x0, y0, z0, 40, config.TPB)
            else:
                print("Selected primitive type has not yet been implemented.")
    else:
        print("Provide either a file name or a desired primitive.")
        return

    print("Initial Bounding Box Dimensions: "+str(origShape.shape))
    origShape = SDF3D(f.condense(origShape, config.BUFFER, config.TPB), tpb=config.TPB)
    if config.NET:
        origShape = f.shell(origShape, config.NET_THICKNESS, config.TPB)
    print("Condensed Bounding Box Dimensions: "+str(origShape.shape))
    
    if config.SUPPORT:
        projected = f.projection(origShape, config.TPB)
        support = f.subtract(f.thicken(origShape, 1), projected, config.TPB)
        support = f.intersection(support, f.translate(support, -1, 0, 0, config.TPB), config.TPB)
        contourPlot(support,30,titlestring='Support',axis ="Z")
        supportPts = genRandPoints(xHeight(support, config.TPB), config.SUPPORT_THRESH)
        supportVoronoi = voronize(support, supportPts, config.SUPPORT_CELL, 0, scale, name = "Support", sliceAxis = "Z")
        if config.PERFORATE: 
            explosion = f.union(
                explode(supportPts),
                f.translate(explode(supportPts), -1, 0, 0, config.TPB),
                config.TPB,
            )
            explosion = f.union(explosion, f.translate(explosion, 0, 1, 0, config.TPB), config.TPB)
            explosion = f.union(explosion, f.translate(explosion, 0, 0, 1, config.TPB), config.TPB)
            supportVoronoi = f.subtract(explosion, supportVoronoi, config.TPB)
        table = f.subtract(
            f.thicken(origShape, 1),
            f.intersection(
                f.translate(f.subtract(origShape, f.translate(origShape, -3, 0, 0, config.TPB), config.TPB), -1, 0, 0, config.TPB),
                projected,
                config.TPB,
            ),
            config.TPB,
        )
        supportVoronoi = f.union(table, supportVoronoi, config.TPB)
        findVol(supportVoronoi,scale,config.MAT_DENSITY,"Support")
    
    if config.MODEL:
        if config.AESTHETIC:
            objectPts = genRandPoints(f.shell(origShape, 5, config.TPB), config.MODEL_THRESH)
        else:
            objectPts = genRandPoints(origShape,config.MODEL_THRESH)
        print("Points Generated!")
        objectVoronoi = voronize(origShape, objectPts, config.MODEL_CELL, config.MODEL_SHELL, scale, name="Object")
        findVol(objectVoronoi,scale,config.MAT_DENSITY,"Object") #in mm^3
        if config.AESTHETIC:
            objectVoronoi = f.union(objectVoronoi, f.thicken(origShape, -5), config.TPB)
    shortName = shortName+"_Voronoi"
    if config.SUPPORT and config.MODEL:
        complete = f.union(objectVoronoi, supportVoronoi, config.TPB)
        if config.IMG_STACK:
            generateImageStack(objectVoronoi,[255,0,0],supportVoronoi,[0,0,255],name = shortName)
    elif config.SUPPORT:
        complete = supportVoronoi
        if config.IMG_STACK:
            generateImageStack(supportVoronoi,[0,0,0],supportVoronoi,[0,0,255],name = shortName)
    elif config.MODEL:
        complete = objectVoronoi
        if config.IMG_STACK:
            generateImageStack(objectVoronoi,[255,0,0],objectVoronoi,[0,0,0],name = FILE_NAME[:-4])
    slicePlot(complete, origShape.shape[0]//2, titlestring='Full Model', axis = "X")
    slicePlot(complete, origShape.shape[1]//2, titlestring='Full Model', axis = "Y")
    slicePlot(complete, origShape.shape[2]//2, titlestring='Full Model', axis = "Z")
    
    print("That took "+str(round(time.time()-start,2))+" seconds.")
    UIP = input("Would you like the .ply for this iteration? [Y/N]")
    if UIP == "Y" or UIP == "y":
        if modelImport:
            fn = shortName
        else:
            fn = input("What would you like the file to be called?")
        print("Generating Model...")
        if config.SEPARATE_SUPPORTS and config.SUPPORT and config.MODEL:
            if config.SMOOTH:
                objectVoronoi = f.smooth(objectVoronoi, tpb=config.TPB)
            generateMesh(objectVoronoi,scale,modelName=fn)
            print("Generating Supports...")
            if config.SMOOTH:
                supportVoronoi = f.smooth(supportVoronoi, tpb=config.TPB)
            generateMesh(supportVoronoi,scale,modelName=fn+"Support")
        else:
            if config.SMOOTH:
                complete = f.smooth(complete, tpb=config.TPB)
            generateMesh(complete,scale,modelName=fn)
        if config.INVERSE and config.MODEL:
            print("Generating Inverse...")
            inv = f.subtract(objectVoronoi, origShape, config.TPB)
            if config.SMOOTH:
                inv = f.smooth(inv, tpb=config.TPB)
            print("Generating Mesh...")
            generateMesh(inv,scale,modelName=fn+"Inv")

if __name__ == '__main__':
    main(PipelineConfig())
