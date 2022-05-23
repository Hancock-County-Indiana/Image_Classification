"""
#Created by Amanda Roberts on 04/06/2022.
#Last edited 05/10/2022
#Code is using Python 3.7
#Status: Runs and produces expected result
#
#This code adds a projection to the imageai outputs and creates centerpoints
#for the boxes if there are any in the output image
"""

import shutil
from osgeo import gdal, osr
import os
import pandas as pd
import re


#creates ground control points from the preprocessed data and projects the 
#imageai outputs to match their preprocessed data counterpart.  Also creates
#centerpoints for the bounding boxes
# inFilePath - path to the unprojected imageai output
# outFilePath - path to where the projected data will go
# matchFilePath - path to the preprocessed image
# boxCSVpath - path to where the csv with box points is located
def makeProjection(inFileFolder, outFileFolder, matchFileFolder, boxCSVFolder, fileName):
    
    #set up the paths
    inFilePath = inFileFolder + "\\" + fileName
    outFilePath = outFileFolder + "\\" + fileName
    matchFilePath = matchFileFolder + "\\" + fileName
    boxCSVpath = boxCSVFolder + "\\boxes1" + file[0:-4] + ".csv"
    
    #create a copy of the original data 
    shutil.copy(inFilePath, outFilePath)
    outds = gdal.Open(outFilePath, gdal.GA_Update)
    #open and retrieve projection information from the preprocess image
    matchds = gdal.Open(matchFilePath)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(2965) #NAD_1983_Indiana_East_ftUS
    
    #get the corner coordinates, pixel resolution, and the raster dimensions
    ulx, xres, xskew, uly, yskew, yres = matchds.GetGeoTransform()
    rasX = matchds.RasterXSize
    rasY = matchds.RasterYSize
    lrx = ulx + (rasX * xres)
    lry = uly + (rasY * yres)
    
    
    #create the ground control points that will be used to project the imageai output
    # Format: [map x-coordinate(longitude)], [map y-coordinate (latitude)], [elevation],
    # [image column index(x)], [image row index (y)]
    gcps = [gdal.GCP(ulx, uly, 0, 0, 0), #upper left/UL
    gdal.GCP(lrx, uly, 0, rasX, 0), #upper right/UR
    gdal.GCP(ulx, lry, 0, 0, rasY), #bottom left/BL
    gdal.GCP(lrx, lry, 0, rasX, rasY)] #bottom right/BR
    
    
    #apply the GCPs to the open output file
    outds.SetGCPs(gcps, sr.ExportToWkt())
    
    #close the output file in order to be able to work with it in other programs
    outds = None
    
    #open bounding box csv
    boxCSV = pd.read_csv(boxCSVpath)
    #remove the index column since pandas creates one automatically
    boxCSV.drop('Unnamed: 0', axis = 1, inplace = True)
    boxCopy = pd.DataFrame().reindex_like(boxCSV)
    
    #checks if the table is empty and skips the box projections if it is
    if boxCopy.empty:
        pass
    #if table isn't empty, project the coordinates using the data from before
    else:
        boxCopy.iloc[:, 0] = boxCSV.iloc[:, 0] * xres + ulx
        boxCopy.iloc[:, 2] = boxCSV.iloc[:, 2] * xres + ulx
        boxCopy.iloc[:, 1] = boxCSV.iloc[:, 1] * yres + uly
        boxCopy.iloc[:, 3] = boxCSV.iloc[:, 3] * yres + uly

        boxCopy.to_csv(outFileFolder + r"\\projectBox" + file[0:-4] + ".csv")
        
        #make new dataframe that has the averaged x and y values in it to make
        #centerpoints of the boxes
        numRecords = boxCopy.shape[0]
        pointsDF = pd.DataFrame(index = range(numRecords), columns = range(2))
        pointsDF.iloc[:, 0] = (boxCopy.iloc[:, 0] + boxCopy.iloc[:, 2])/2
        pointsDF.iloc[:, 1] = (boxCopy.iloc[:, 1] + boxCopy.iloc[:, 3])/2
        
        pointsDF.to_csv(outFileFolder + r"\\projectPoints" + file[0:4] + ".csv")
    

if __name__ == "__main__":

    #this line is needed to make sure gdal loads in right; change to the folder
    #your IDE stores packages in
    #CHANGEME
    os.environ['PROJ_LIB'] = r'C:\Users\aroberts\.conda\envs\python-gis\Library\share\proj'
    
    #CHANGEME
    fileFolder = r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\allfishout"
    outputFolder = r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\allfishoutproj"
    matchFolder = r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\ras1clips"
    boxFolder = r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\allfishout"
    
    #list all of the files in the folder where the non-projected images are
    origFileList = os.listdir(fileFolder)
    
    
    for file in origFileList:
        #if the file is a .tif, set up the paths and run makeProjection    
        if file.endswith(".tif"): 
            num = re.findall(r'\d+', file)[-1]
            if int(num)%50 == 0:
                print(file)
            #make function return boxes and points and save to a bigger list?
            makeProjection(fileFolder, outputFolder, matchFolder, boxFolder, file)






