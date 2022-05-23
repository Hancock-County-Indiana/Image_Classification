# -*- coding: utf-8 -*-
"""
#Created by Amanda Roberts on 03/01/2022.
#Last edited 05/02/2022
#Code is using Python 3.7
#Status: Runs and produces expected result
#
#This code runs the imageai detection using a trained model created in FirstCustomTraining.py
#Search for "CHANGEME" to locate file paths that need to be changed
"""

import os
import pandas as pd
from imageai.Detection.Custom import CustomObjectDetection
import time


if __name__ == "__main__":
    
    startTime = time.time()
    #set up the model
    detector = CustomObjectDetection()
    detector.setModelTypeAsYOLOv3()
    #Point script to the training model created during the training step  
    #Use the model with the latest timestamp in the model folder
    #CHANGEME
    detector.setModelPath(r"Z:\GIS\General\map_room\GIS\Scripts\Updated_Imageai_Model\detection_model-ex-028--loss-0021.472.h5")
    #Point script to the json file created in training
    #It should be in the json folder and will be named detection_config.json
    #CHANGEME
    detector.setJsonPath(r"Z:\GIS\General\map_room\GIS\Scripts\Updated_Imageai_Model\detection_config.json")
    detector.loadModel()
    
    #put the path to the folder with the images that need headstone IDs
    #CHANGEME
    imagesDir = r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\ras1clips"
    fileList = os.listdir(imagesDir)
    
    for file in fileList:
        headstoneBoxes = list()
        fileStartTime = time.time()
        #if the file is a .tif, run the imageai model on it
        if file.endswith('.tif'):
            filePath = imagesDir + "\\" + file
            #CHANGEME
            outPath = r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\allfishout2\\" + file 
            detections = detector.detectObjectsFromImage(input_image=filePath, output_image_path=outPath, display_percentage_probability=False, display_object_name=False)
            #for each box created, add the corners of it to a list
            for detection in detections:
                boxPoints = detection["box_points"]
                headstoneBoxes.append(boxPoints)
            
            #convert the box corners list to a table and save
            df1 = pd.DataFrame(headstoneBoxes)
            #CHANGEME
            df1.to_csv(r"Z:\GIS\General\map_room\GIS\Scripts\Test_imageai_outputs\allfishout2\boxes1" + file[0:-4] + ".csv")
            print(str((time.time() - fileStartTime)/60))
    print(str((time.time() - startTime)/60))
            
            
            
            