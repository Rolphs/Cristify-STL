import os #Just used to set up file directory
import time
import numpy as np
import Frep as f
import userInput as u
from voronize import voronize
from SDF3D import SDF3D, xHeight
from pointGen import genRandPoints, explode
from meshExport import generateMesh
from analysis import findVol
from visualizeSlice import slicePlot, contourPlot, generateImageStack
from voxelize import voxelize

def main():
    start = time.time()
    try:    os.mkdir(os.path.join(os.path.dirname(__file__),'Output')) #Creates an output folder if there isn't one yet
    except: pass
    try:    FILE_NAME = u.FILE_NAME
    except: FILE_NAME = ""
    try:    PRIMITIVE_TYPE = u.PRIMITIVE_TYPE #Checks to see if a primitive type has been set
    except: PRIMITIVE_TYPE = ""
    modelImport = False
    scale = [1,1,1]
    if not u.MODEL and not u.SUPPORT:
        print("You need at least the model or the support structure.")
        return
    if FILE_NAME != "":
        shortName = FILE_NAME[:-4]
        modelImport = True
        try:    filepath = os.path.join(os.path.dirname(__file__), 'Input',FILE_NAME)
        except: 
            print("Input file not found.") 
            return
        res = u.RESOLUTION-u.BUFFER*2
        origShape, objectBox = voxelize(filepath, res, u.BUFFER, u.TPB)
        gridResX, gridResY, gridResZ = origShape.shape
        scale[0] = objectBox[0]/(gridResX-u.BUFFER*2)
        scale[1] = max(objectBox[1:])/(gridResY-u.BUFFER*2)
        scale[2] = scale[1]
    elif PRIMITIVE_TYPE != "":
        shortName = PRIMITIVE_TYPE
        if PRIMITIVE_TYPE == "Heart":
            x0 = np.linspace(-1.5,1.5,u.RESOLUTION)
            y0, z0 = x0, x0
            origShape = f.heart(x0, y0, z0, 0, 0, 0, u.TPB)
        elif PRIMITIVE_TYPE == "Egg":
            x0 = np.linspace(-5,5,u.RESOLUTION)
            y0, z0 = x0, x0
            origShape = f.egg(x0, y0, z0, 0, 0, 0, u.TPB)
            #eggknowledgement to Molly Carton for this feature.
        else:
            x0 = np.linspace(-50,50,u.RESOLUTION)
            y0, z0 = x0, x0
            if PRIMITIVE_TYPE == "Cube":
                origShape = f.rect(x0, y0, z0, 80, 80, 80, tpb=u.TPB)
            elif PRIMITIVE_TYPE == "Silo":
                origShape = f.union(
                    f.sphere(x0, y0, z0, 40, u.TPB),
                    f.cylinderY(x0, y0, z0, -40, 0, 40, u.TPB),
                    u.TPB,
                )
            elif PRIMITIVE_TYPE == "Cylinder":
                origShape = f.cylinderX(x0, y0, z0, -40, 40, 40, u.TPB)
            elif PRIMITIVE_TYPE == "Sphere":
                origShape = f.sphere(x0, y0, z0, 40, u.TPB)
            else:
                print("Selected primitive type has not yet been implemented.")
    else:
        print("Provide either a file name or a desired primitive.")
        return

    print("Initial Bounding Box Dimensions: "+str(origShape.shape))
    origShape = SDF3D(f.condense(origShape, u.BUFFER, u.TPB), tpb=u.TPB)
    if u.NET:
        origShape = f.shell(origShape, u.NET_THICKNESS, u.TPB)
    print("Condensed Bounding Box Dimensions: "+str(origShape.shape))
    
    if u.SUPPORT:
        projected = f.projection(origShape, u.TPB)
        support = f.subtract(f.thicken(origShape, 1), projected, u.TPB)
        support = f.intersection(support, f.translate(support, -1, 0, 0, u.TPB), u.TPB)
        contourPlot(support,30,titlestring='Support',axis ="Z")
        supportPts = genRandPoints(xHeight(support, u.TPB), u.SUPPORT_THRESH)
        supportVoronoi = voronize(support, supportPts, u.SUPPORT_CELL, 0, scale, name = "Support", sliceAxis = "Z")
        if u.PERFORATE: 
            explosion = f.union(
                explode(supportPts),
                f.translate(explode(supportPts), -1, 0, 0, u.TPB),
                u.TPB,
            )
            explosion = f.union(explosion, f.translate(explosion, 0, 1, 0, u.TPB), u.TPB)
            explosion = f.union(explosion, f.translate(explosion, 0, 0, 1, u.TPB), u.TPB)
            supportVoronoi = f.subtract(explosion, supportVoronoi, u.TPB)
        table = f.subtract(
            f.thicken(origShape, 1),
            f.intersection(
                f.translate(f.subtract(origShape, f.translate(origShape, -3, 0, 0, u.TPB), u.TPB), -1, 0, 0, u.TPB),
                projected,
                u.TPB,
            ),
            u.TPB,
        )
        supportVoronoi = f.union(table, supportVoronoi, u.TPB)
        findVol(supportVoronoi,scale,u.MAT_DENSITY,"Support")
    
    if u.MODEL:
        if u.AESTHETIC:
            objectPts = genRandPoints(f.shell(origShape, 5, u.TPB), u.MODEL_THRESH)
        else:
            objectPts = genRandPoints(origShape,u.MODEL_THRESH)
        print("Points Generated!")
        objectVoronoi = voronize(origShape, objectPts, u.MODEL_CELL, u.MODEL_SHELL, scale, name="Object")
        findVol(objectVoronoi,scale,u.MAT_DENSITY,"Object") #in mm^3
        if u.AESTHETIC:
            objectVoronoi = f.union(objectVoronoi, f.thicken(origShape, -5), u.TPB)
    shortName = shortName+"_Voronoi"
    if u.SUPPORT and u.MODEL:
        complete = f.union(objectVoronoi, supportVoronoi, u.TPB)
        if u.IMG_STACK:
            generateImageStack(objectVoronoi,[255,0,0],supportVoronoi,[0,0,255],name = shortName)
    elif u.SUPPORT:
        complete = supportVoronoi
        if u.IMG_STACK:
            generateImageStack(supportVoronoi,[0,0,0],supportVoronoi,[0,0,255],name = shortName)
    elif u.MODEL:
        complete = objectVoronoi
        if u.IMG_STACK:
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
        if u.SEPARATE_SUPPORTS and u.SUPPORT and u.MODEL:
            if u.SMOOTH:
                objectVoronoi = f.smooth(objectVoronoi, tpb=u.TPB)
            generateMesh(objectVoronoi,scale,modelName=fn)
            print("Generating Supports...")
            if u.SMOOTH:
                supportVoronoi = f.smooth(supportVoronoi, tpb=u.TPB)
            generateMesh(supportVoronoi,scale,modelName=fn+"Support")
        else:
            if u.SMOOTH:
                complete = f.smooth(complete, tpb=u.TPB)
            generateMesh(complete,scale,modelName=fn)
        if u.INVERSE and u.MODEL:
            print("Generating Inverse...")
            inv = f.subtract(objectVoronoi, origShape, u.TPB)
            if u.SMOOTH:
                inv = f.smooth(inv, tpb=u.TPB)
            print("Generating Mesh...")
            generateMesh(inv,scale,modelName=fn+"Inv")

if __name__ == '__main__':
    main()