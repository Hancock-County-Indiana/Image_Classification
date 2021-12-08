# -*- coding: utf-8 -*-
"""
Created by Amanda Roberts on 09/14/2021
Last edited 12/06/2021
Code is using Python 3.7 

This code identify cemetaries and each of their headstones using the
 Random Forest algorithm and SLIC segmentation method
Export out coordinates to a csv; label gravestones by cemetary then number in cemetary
#FUTURE: watershed segmentation on gravestones
"""


import gdal
import numpy as np
import time
import rasterio
import geopandas as gpd
import pandas as pd
from rasterio.features import shapes


#CreateHeadstonePoint - process that takes a classified image, masks it into
#       headstones and not headstones, creates polygons from the headstone
#       pixels, creates a point in the centrod of the polygons, and assigns an
#       ID code to each headstone
# raster - classified .tif image of the cemetary site
# cemName - name of the cemetary to be used when accessing file paths/file names
# cemCode - four letter code to refer to the cemetary as in its ID code
# cemClass - the value of the class that represents headstones
def CreateHeadstonePoint(raster, cemName, cemCode, cemClass):
    
    #time how long it takes to run the function
    startTime = time.time()
    
    #get the file path from the raster
    rasterReverse = raster[::-1]
    fileOutPathRev = rasterReverse.split("\\", 1)
    fileOutPath = fileOutPathRev[1]
    fileOutPath = fileOutPath[::-1]

    #prepare needed data
    file = gdal.Open(raster)
    #file = rasterio.open(raster)
    fileArr = file.ReadAsArray()
    
    #reclassify raster into headstones and not headstones
    fileArr[np.where(fileArr != cemNum)] = 5
    fileArr[np.where(fileArr == cemNum)] = 1
    fileArr[np.where(fileArr == 5)] = 0
    
    #save masked raster to computer
    driver = gdal.GetDriverByName('GTiff')
    driver.Register()
    fileOut = fileOutPath + r"\maskedRaster" + cemName + ".tif"
    xPixels = file.RasterXSize
    yPixels = file.RasterYSize
    dataset = driver.Create(fileOut, xPixels, yPixels, 1, gdal.GDT_Float32)
    dataset.SetProjection(file.GetProjection())
    dataset.SetGeoTransform(file.GetGeoTransform())
    dataset.GetRasterBand(1).WriteArray(fileArr)
    dataset.FlushCache()

    #vectorize the raster
    mask = None
    inFile = fileOutPath + r"\maskedRaster" + cemName + ".tif"
    with rasterio.Env():
        with rasterio.open(inFile) as src:
            image = src.read(1)
            results = ({'properties': {'rasVal': v}, 'geometry': s}
                       for i, (s,v) in enumerate(shapes(image, mask = mask, transform = src.transform)))
    
    #remove polygons that are too small or large or are not headstones
    # and save the file
    geoms = list(results)
    rasToPoly = gpd.GeoDataFrame.from_features(geoms)
    rasToPoly = rasToPoly.set_crs(epsg=2965)
    rasToPoly["Area"] = rasToPoly['geometry'].area
    rasToPoly = rasToPoly[rasToPoly.Area < 125.0]
    rasToPoly = rasToPoly[rasToPoly.Area > .5]
    rasToPoly = rasToPoly[rasToPoly.rasVal == 1]
    rasToPoly.to_file(fileOutPath + r"\vectorGraves" + cemName + ".shp")
    
    #copy geodataframe
    headstonesDF = rasToPoly.copy()
    #create points based off of the centroid of the polygons
    headstonesDF['geometry'] = headstonesDF['geometry'].centroid
    #set projection
    headstonesDF = headstonesDF.set_crs(epsg=2965)
    #remove any NaN values in the geodataframe
    headstones = headstonesDF.dropna()
    
    #create id for headstones that contain a 4 letter cemetary code and 5 digit
    # gravestone number ie CEMS00001
    headstones["graveID"] = ""
    headstones = headstones.reset_index(drop=True)
    i = 1
    for record in headstones["graveID"]:
        if i < 10:
            graveID = cemCode + "0000" + str(i)
            headstones.at[i-1, "graveID"] = graveID 
        elif i < 100:
            graveID = cemCode + "000" + str(i)
            headstones.at[i-1, "graveID"] = graveID
        elif i < 1000:
            graveID = cemCode + "00" + str(i)
            headstones.at[i-1, "graveID"] = graveID
        elif i < 10000:
            graveID = cemCode + "0" + str(i)
            headstones.at[i-1, "graveID"] = graveID
        else:
            graveID = cemCode + str(i)
            headstones.at[i-1, "graveID"] = graveID
        i+=1
        
    #save headstone points to file
    headstones.to_file(fileOutPath + r"\headstonePoints" + cemName + ".shp")
    headstones.to_csv(fileOutPath + r"\headstones" + cemName + ".csv")

    #print out time taken to run function in minutes
    print(str((time.time() - startTime)/60) + cemName)


if __name__ == "__main__":

    # read in schema
    schemaIn = pd.read_csv(r"C:\Users\aroberts\Documents\Code\raster_classification\Cemetaries\Code\headstoneIDSchema.csv")
    #assign columns in schema to variables for easy access
    fileInList = schemaIn.iloc[:,1]
    cemNamesList = schemaIn.iloc[:, 2]
    cemCodesList = schemaIn.iloc[:, 3]
    cemClassList = schemaIn.iloc[:, 4]
    #determine how many cemetaries are in the schema file
    listLen = fileInList.size
    #time how long the loop takes
    startTimeWhole = time.time()
    
    #run the function to create headstones on each item in the schema
    for num in range(listLen):
        #assign the cemetary variables from the schema file
        item = fileInList[num]
        name = cemNamesList[num]
        cemAbbr = cemCodesList[num]
        cemNum = cemClassList[num]
        CreateHeadstonePoint(item, name, cemAbbr, cemNum)
    
    #print out how long it took the loop to run in minutes
    print((time.time()-startTimeWhole)/60)



