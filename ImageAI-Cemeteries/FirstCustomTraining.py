"""
#Created by John Milburn on 02/23/2022.
#Last edited 03/11/2022
#Code is using Python 3.7
#Status: Runs and produces expected result
#
#This code sets up and runs the training algorithm to create an imageai model
#Search for "CHANGEME" to locate file paths that need to be changed
"""

from imageai.Detection.Custom import DetectionModelTrainer

#set up the trainer to run
trainer = DetectionModelTrainer()
trainer.setModelTypeAsYOLOv3()
#CHANGEME
trainer.setDataDirectory(data_directory= r"Z:\GIS\General\map_room\GIS\Scripts\Training_Data\imageAI")
trainer.setTrainConfig(object_names_array=["headstone", "not_headstone"], batch_size=4, 
num_experiments=50, train_from_pretrained_model=r"Z:\GIS\General\map_room\GIS\Scripts\imageai_code\supporting\pretrained-yolov3.h5")
#run the training
trainer.trainModel()