#The script generates the datasets needed for the GLM Largest-Flash Viewer in pkl and csv formats


import subprocess as sp
import sys
import os
import netCDF4 as nc
from datetime import timedelta
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


args = sys.argv
tnow1 = args[1] #Import datetime object as function argument from glm-control.py
tnow2 = args[2] #Import datetime object as function argument from glm-control.py


tnow = datetime.strptime(tnow1+tnow2, '%Y-%m-%d%H:%M:%S') #Converting into datetimes


#constants
tdata_loc = '/home/kevin.thiel/Desktop/big-flash/temp-data/'
dset_loc = '/home/kevin.thiel/Desktop/big-flash/'
f_loc = '/home/kevin.thiel/Desktop/big-flash/'




#STEP 1, download the GLM data from google cloud
#tnow = datetime.now() #Getting the current time
tdelta = timedelta(minutes=10) #Creating a time delta

#Getting the start of the window that will be used
tstart = tnow - timedelta(minutes=tnow.minute % 10, seconds=tnow.second, microseconds=tnow.microsecond) - tdelta
tend = tnow - timedelta(minutes=tnow.minute % 10, seconds=tnow.second, microseconds=tnow.microsecond)


year = tstart.strftime('%Y')
doy = tstart.strftime("%j")
hr = tstart.strftime("%H")
min = tstart.strftime("%M")


cmd = 'gsutil -m cp gs://gcp-public-data-goes-16/GLM-L2-LCFA/'+year+'/'+doy+'/'+hr+'/OR_GLM-L2-LCFA_G16_s'+year+doy+hr+min[0]+'* '+tdata_loc
p = sp.Popen(cmd,shell=True)
p.wait()


#STEP 2, read and cycle through the files to find the biggest flash area

files = os.listdir(tdata_loc) #Listing all of the files in the directory

#Dummy values that will be used to start for the flash size
max_size = -999
size_lat = np.nan
size_lon = np.nan


#Searching through each file for the biggest flash
for i in files:
	file = nc.Dataset(tdata_loc+i,'r')
	flash_count = file.variables['flash_count'][:]
	
	if flash_count > 0: #Making sure there are flashes to serach through in the file
		area = file.variables['flash_area'][:]*1e-6 #Converting to square km's
		
		if np.max(area) > max_size: #Checking if the max size in the file is larger than the current largest flash
			area_loc = np.where(area == np.max(area))[0]
			area_loc = area_loc[0] #If there's duplicates, we're only taking the first one
			
			max_size = area[area_loc]
			size_lat = file.variables['flash_lat'][area_loc]
			size_lon = file.variables['flash_lon'][area_loc]
			
			
	file.close #closing the file			
			
			
#Making the dataframe to add onto the current one
newdict = {'Lat':[size_lat],'Lon':[size_lon],'Size':[max_size],'Time':[tend]}
newdf = pd.DataFrame(data=newdict)
newdf = newdf.set_index('Time')

olddf = pd.read_csv(dset_loc+'dataset2019.csv')
olddf = olddf.set_index('Time')
updated_df = pd.concat((olddf,newdf),axis=0, sort=True) #Adding the new data		
#updated_df.to_pickle(dset_loc+'dataset2018.pkl') #Saving the new dataframe
updated_df.to_csv(dset_loc+'dataset2019.csv') #Public dataset


cmd = 'rm '+tdata_loc+'*' #Removing the previous files
p = sp.Popen(cmd,shell=True)
p.wait()
