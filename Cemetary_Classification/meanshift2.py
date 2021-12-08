# -*- coding: utf-8 -*-
"""
Created by Amanda Roberts on 10/05/2021
Last edited 12/07/2021
Code is using Python 3.7 

This code runs the meanshift algorithm on a cemetary using a predefined
 bandwidth and saves the results
"""


from sklearn.cluster import MeanShift
from scipy.ndimage import gaussian_filter
import numpy as np
import gdal
import time
import pandas as pd

#MeanShiftCalc - runs the meanshift algorithm on the given image until it
#       has either 3, 4, or 5 classes
#
# INPUTS 
# inImage - .tif file of the cemetary to be classified
# bandwidth - starting integer to give to the meanshift algorithm (around 20)
#
# OUTPUTS
# resultImage - classified raster with 3, 4, or 5 classes
def MeanShiftCalc(inImage, bandwidth):
    
    #check if bandwidth is a positive integer and does not run if not
    if bandwidth <= 0:
        pass
    #create an empty raster based off of the opened one
    nbands = inImage.RasterCount 
    data = np.empty((inImage.RasterXSize*imageOpen.RasterYSize, nbands))
    for i in range(1, nbands + 1):
        band = inImage.GetRasterBand(i).ReadAsArray()
        band = gaussian_filter(band, sigma = 1)
        data[:, i - 1] = band.flatten()
        
    
    #run the meanshift algorithm
    ms = MeanShift(bandwidth = bandwidth, bin_seeding = True, n_jobs = -1)
    ms.fit(data)
    labels = ms.labels_
    labelsUnique = np.unique(labels)
    
    #if there is less than 3 or more than 5 classes, rerun this function
    # otherwise, assign the meanshift results to the empty raster
    if len(labelsUnique) < 3:
        resultImage = MeanShiftCalc(inImage, bandwidth - 3)
    elif len(labelsUnique) > 5:
        resultImage = MeanShiftCalc(inImage, bandwidth + 1)
    else:
        resultImage = labels.reshape((inImage.RasterYSize, inImage.RasterXSize))
    
    return resultImage


if __name__ == "__main__":

    #time how long it takes
    startTime = time.time()
    
    #read in the schema file with the file locations
    schemaLoc = r"C:\Users\aroberts\Documents\Code\raster_classification\Cemetaries\Code\meanshiftSchema2.csv"
    schemaIn = pd.read_csv(schemaLoc)
    imageFileList = schemaIn.iloc[:, 1]
    imageOutList = schemaIn.iloc[:, 2]
    cemNameList = schemaIn.iloc[:, 3]
    
    #create a counter variable to access schema locationis
    j = 0
    
    #run the function and save results on each item in the schema file
    for imageFile in imageFileList:
        
        #open the raster image
        driverTiff = gdal.GetDriverByName('GTiff')
        imageOpen = gdal.Open(imageFile)
        
        #run the meanshift algorithm
        resultImage = MeanShiftCalc(imageOpen, 19)
        
        #write the created raster to the computer
        imageOutLoc = imageOutList[j]
        imageOut = driverTiff.Create(imageOutLoc, imageOpen.RasterXSize, imageOpen.RasterYSize, 1, gdal.GDT_Float32)
        imageOut.SetGeoTransform(imageOpen.GetGeoTransform())
        imageOut.SetProjection(imageOpen.GetProjection())
        imageOut.GetRasterBand(1).SetNoDataValue(-9999.0)
        imageOut.GetRasterBand(1).WriteArray(resultImage)
        imageOut = None
        imageOpen = None
        
        #print the time it took to run this iteration
        loopTime = ((time.time() - startTime)/60)
        cemName = cemNameList[j]
        print(str(loopTime) + cemName)
        j += 1
    
    #print the time it took to run all cemetaries
    print((time.time() - startTime)/60)


