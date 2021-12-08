# -*- coding: utf-8 -*-
"""
Created by Amanda Roberts on 10/28/2021
Last edited 12/08/2021
Code is using Python 3.7 

This code compares headstone polygons and points created by two different classifications and
deletes any with no overlap
"""

import pandas as pd
import geopandas as gpd
import time

#CombinePoints - takes output from two different classification methods and 
#       compares them against each other to eliminate points that don't overlap
#       between the two functions
#
#pointsIn1 - points created by one classification algorithm
#pointsIn2 - points created by the other classification algorithm
#polygonsIn1 - polygons created by one classification algorithm
#polygonsIn2 - polygons created by the other classification algorithm
#cemName - name of the cemetary  
def CombinePoints(pointsIn1, pointsIn2, polygonsIn1, polygonsIn2, cemName):
    
    #time how long it takes to run
    funcTime = time.time()
    
    #get the file path minus the file name from an input
    filePathRev = pointsIn1[::-1]
    outFile = filePathRev.split("\\", 1)
    fileOutPath = outFile[1]
    fileOutPath = fileOutPath[::-1]
    
    #open vector files
    points1 = gpd.read_file(pointsIn1)
    points2 = gpd.read_file(pointsIn2)
    polygons1 = gpd.read_file(polygonsIn1)
    polygons2 = gpd.read_file(polygonsIn2)
    
    #create new point file where the points from the second set of results overlap the polygons from the first
    joinedPointPoly1 = gpd.sjoin(points2, polygons1, how = "left", lsuffix = "l", rsuffix = "r")
    joinedPointPoly1 = joinedPointPoly1.dropna()
    
    #create new point file where the points from the first set of results overlap the polygons from the second
    joinedPointPoly2 = gpd.sjoin(points1, polygons2, how = "left", lsuffix = "l", rsuffix = "r")
    joinedPointPoly2 = joinedPointPoly2.dropna()
    
    #save outputs to computer
    joinedPointPoly1.to_file(fileOutPath + r"/combine1" + cemName + ".shp")
    joinedPointPoly2.to_file(fileOutPath + r"/combine2" + cemName + ".shp")
    
    #print how long it took to run this function in minutes    
    print(str((time.time() - funcTime)/60))


if __name__ == "__main__":

    #time how long it takes to run the whole thing
    startTimeWhole = time.time()
    
    #read in schema file and assign to variables
    schemaLoc = r"C:\Users\aroberts\Documents\Code\raster_classification\Cemetaries\Code\combinePointsSchema.csv"
    schemaIn = pd.read_csv(schemaLoc)
    points1File = schemaIn.iloc[:, 1]
    points2File = schemaIn.iloc[:, 2]
    polygons1File = schemaIn.iloc[:, 3]
    polygons2File = schemaIn.iloc[:, 4]
    cemNameList = schemaIn.iloc[:, 5]
    listLen = points1File.size
    
    #run the function on each item in the schema
    for num in range(listLen):
        #assign the values from the schema file to variables
        poin1 = points1File[num]
        poin2 = points2File[num]
        poly1 = polygons1File[num]
        poly2 = polygons2File[num]
        cem = cemNameList[num]
        CombinePoints(poin1, poin2, poly1, poly2, cem)
    
    #print how long it took to run everything in minutes    
    print(str((time.time() - startTimeWhole)/60))




