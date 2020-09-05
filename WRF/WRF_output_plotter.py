################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This script reads and plots data from weather research and 
# forecast (WRF) data taken from the coastal urban environmental
# research group (CUERG) website
#
################################################################
#
#
from netCDF4 import Dataset
import numpy as np
import os,datetime,timezonefinder,pytz
import matplotlib.pyplot as plt

##########################################################
# Selecting a WRF file
##########################################################
#
wrf_dir = '/Volumes/MacOS Ext/WRF_files/2019_outputs/' # local WRF repository
wrf_dir_files = [ii+'/' for ii in os.listdir(wrf_dir) if os.path.isdir(wrf_dir+ii)] # collect WRF files
wrf_dir_files.sort() # sort them (by date is defauly)
wrf_folder = wrf_dir+wrf_dir_files[0] # take the first folder
wrf_datafiles   = np.array(os.listdir(wrf_folder)) # get datafiles from WRF folder
wrf_datafiles_args = np.argsort([datetime.datetime.strptime(ii.split('wrfout_d')[1][3:],'%Y-%m-%d_%H:%M:%S') for ii in wrf_datafiles if ii.startswith('wrfout')]) # sorting by datetimes
wrf_datafiles = np.array([ii for ii in wrf_datafiles if ii.startswith('wrfout')])[wrf_datafiles_args]
wrf_datafiles = [ii for ii in wrf_datafiles if ii.split('_')[1]=='d03']
wrf_dates = [datetime.datetime.strptime(ii.split('wrfout_d03_')[1],'%Y-%m-%d_%H:%M:%S') for ii in wrf_datafiles] # get datetimes from file names

##########################################################
# Getting time-series data
# for a particular pixel (aligned with CCNY tower, here)
##########################################################
#
ccny_coords = [-73.949256,40.819156,'CCNY'] # coordinates of CCNY tower

tf = timezonefinder.TimezoneFinder() # timezone library for shifting to local time

temp_array,Rn_array,wrf_t_vec = [],[],[]
U_vert,H_vert = [],[]
#################################
# NOTE BELOW: the 6 file lag - 
# this is the spin-up time, which 
# we want to skip
#################################
#
for t_indx in range(6,len(wrf_dates)):
    wrf_file = wrf_datafiles[t_indx] # WRF filename
    data = Dataset(wrf_folder+wrf_file) # read data from WRF file

    # uncomment below to print out all variable names and descriptions
    if t_indx==6:
        for ii in data.variables.keys():
            if data.variables[ii].ncattrs()!=[]:
                # print variable names, descriptions, and data shape (shape helps determine plot methods)
                print('{0} - {1} ({2})'.format(ii,data.variables[ii].description,data.variables[ii].shape)) 
    
    ######################################
    # below we're deriving net radiation
    ######################################
    #
    SW_IN  = data.variables['SWDOWN'][:].data # incoming shortwave data
    SW_OUT = data.variables['ALBEDO'][:]*SW_IN # outgoing shortwave
    LW_IN  = data.variables['GLW'][:].data # incoming longwave
    LW_OUT = data.variables['EMISS'][:]*(5.670374419*np.power(10.0,-8.0))*np.power(data.variables['TSK'][:].data,4.0) # outgoing longwave
    Rn_wrf = (SW_IN-SW_OUT) + (LW_IN - LW_OUT) # surface net radiation

    lat_wrf = data.variables['XLAT'][:] # lat coordinate
    lon_wrf = data.variables['XLONG'][:] # lon coordinate
    
    ######################################
    # find closest pixel to CCNY tower
    ######################################
    #
    ccny_indx = np.unravel_index(np.argmin(np.abs(lon_wrf-ccny_coords[0])+np.abs(lat_wrf-ccny_coords[1])),np.shape(lat_wrf))
    T2_ccny = data.variables['T2'][:][ccny_indx] #index of CCNY tower
    Rn_ccny = Rn_wrf[ccny_indx] #index of CCNY tower
    
    ######################################
    # grab 2D profiles (potentials)
    ######################################
    #
    U = data.variables['U'][:][0,:,ccny_indx[1],ccny_indx[2]] # horizontal velocity vertical profile
    geopot_h = ((((data.variables['PHB'][:][0,:,ccny_indx[1],ccny_indx[2]])[1:]+\
                (data.variables['PHB'][:][0,:,ccny_indx[1],ccny_indx[2]])[:-1])/2.0)+\
               (((data.variables['PHB'][:][0,:,ccny_indx[1],ccny_indx[2]])[1:]+\
                (data.variables['PHB'][:][0,:,ccny_indx[1],ccny_indx[2]])[:-1])/2.0))/9.81 # geopotential heights
    
    ######################################
    # append the variables to arrays
    ######################################
    #
    wrf_t_vec.append(wrf_dates[t_indx]) # time variable
    temp_array.append(T2_ccny) # temperature array
    Rn_array.append(Rn_ccny) # net radiation array
    U_vert.append(U) # vertical velocity array
    H_vert.append(geopot_h) # geopotential heights array
    
timezone_str = tf.certain_timezone_at(lat=np.mean(lat_wrf), lng=np.mean(lon_wrf)) # get time zone for city center
timezone = pytz.timezone(timezone_str) # set time zone

##########################################################
# plotting example WRF data
##########################################################
#
plt.style.use('ggplot')
fig,ax = plt.subplots(figsize=(14,8)) # start figure
local_t_vec = np.subtract(wrf_t_vec,timezone.utcoffset(wrf_t_vec[0])) # correct for local time
ax.plot(local_t_vec,temp_array,label='$T_{air}$',color=plt.cm.Set1(0)) # plot temperature
ax2 = ax.twinx() # plot a twin axis for plotting on the same subplot
ax2.plot(local_t_vec,Rn_array,label='$R_n$',color=plt.cm.Set1(1)) # plot net radiation
ax.legend(loc='upper left',fontsize=16)
ax2.legend(loc='upper right',fontsize=16)
ax2.grid(False)
ax.set_xlabel('Time [yyyy-mm-dd]',fontsize=16)
ax.set_ylabel('Temperature [K]',fontsize=16,color=plt.cm.Set1(0))
ax2.set_ylabel('Net Radiation [W$\cdot$m$^{-2}$]',fontsize=16,color=plt.cm.Set1(1))
ax.set_title('Forecasted Net Radiation and Air Temperature from uWRF',fontsize=16)
plt.show()

fig2,ax2 = plt.subplots(figsize=(14,8)) # start figure
p1 = ax2.contourf(local_t_vec,H_vert[0],np.transpose(U_vert), 20, cmap='hot')
ax2.set_xlabel('Date in {} [mm-dd-HH]'.format(local_t_vec[0].year),fontsize=16)
ax2.set_ylabel('Height [m]',fontsize=16)
cbar = fig2.colorbar(p1)
cbar.set_label('Horizontal Velocity. U [m$\cdot$s$^{-1}$]',fontsize=16)
ax2.set_title('Weather Research and Forecasting Model Vertical Velocity Profile',fontsize=16)
