################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This codes uses FTP to access automated surface observing 
# station (ASOS) data. It plots the resulting first month
# of the year variables: pressures, temperatures, humidities
#
################################################################
#
from ftplib import FTP
import csv,os,datetime
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('ggplot')

########################################
# FTP connection and directory handling
########################################
#
ftp =  FTP('ftp.ncdc.noaa.gov') # ftp access to ncdc.noaa.gov
ftp.login() # anonymous ftp login
ftp.cwd('pub/data/asos-onemin') # change directory to asos-onemin
dirs = ftp.nlst() # list all files in directory
# uncomment below to print out all files/folders in asos-onemin dir
##[print(str(ii)+' '+jj) for ii,jj in enumerate(dirs)] # print dirs/files and their indices
description_files = [ii for ii in dirs if len(ii.split('.'))>1]
for file in description_files:
    if os.path.isfile(file):
        print('already downloaded file: '+file)
        continue
    with open(file, 'wb') as fp:
        ftp.retrbinary('RETR '+file, fp.write) # save non-directory files (readme, etc.)

########################################
# Accessing data files/directories
########################################
#
data_dir_indx = 41 # select index printed out in Python window
ftp.cwd(dirs[data_dir_indx]) # 41 == 6406-2020 [in my particular case]
print('Accessing: {} Folder'.format(dirs[data_dir_indx]))
data_files = ftp.nlst() # list all data files for directory above

########################################
# download ASOS file with all station
# properties (lat/lon/elevation)
########################################
#
ftp.cwd('/pub/data/ASOS_Station_Photos/')
asos_filename = 'asos-stations.txt'
if os.path.isfile(asos_filename):
    print('already downloaded file: '+asos_filename)
else:
    with open(asos_filename, 'wb') as fp:
        ftp.retrbinary('RETR '+asos_filename, fp.write) # save non-directory files (readme, etc.)

station_props,station_header,dash_header = [],[],[]
header_bool,dash_bool = False,False
with open(asos_filename,newline='') as txtfile:
    csvreader = csv.reader(txtfile,delimiter='\t')
    for row in csvreader:
        if len(row)<1:
            continue
        if row[0][0:6]=='NCDCID':
            station_header = row[0]
            header_bool = True
        elif header_bool:
            if dash_bool:
                props = []
                props_iter = 0
                for qq in dash_header:
                    props.append(row[0][props_iter:props_iter+len(qq)+1])
                    props_iter+=len(qq)+1
                station_props.append(props)
            else:
                dash_header = (row[0]).split(' ')
                dash_bool = True
                props_iter = 0
                props = []
                for rr in dash_header:
                    props.append(station_header[props_iter:props_iter+len(rr)+1])
                    props_iter+=len(rr)+1
                station_header = props

# now we have two variables which will help us characterize each
# ground station:
# - station_header - 
#    __this variable contains the header for each station and what each row means
# - station_props -
#    __this variable contains the specific station information (for 900+ stations in USA)


########################################
# Finding a station by coordinates
########################################
#
# if we use a geographic coordinate, we can find
# a specific station that's nearest to that location

my_lat,my_lon = 34.0522,-118.2437 # LA coordinates
##my_lat,my_lon = 40.7128,-74.0060  # NYC coordinates
##my_lat,my_lon = 41.8781,-87.6298  # Chicago coordinates
##my_lat,my_lon = 21.3069,-157.8583 # Honolulu coordinates

station_lats = [float(ii[9]) for ii in station_props]
station_lons = [float(ii[10]) for ii in station_props]

# find the station lat/lon nearest to the input my_lat/my_lon
nearest_indx = np.argmin(np.abs(np.subtract(station_lats,my_lat))+np.abs(np.subtract(station_lons,my_lon)))
print('-----------')
print('The nearest station to {},{} is {} ({}) at {},{}'.\
      format(my_lat,my_lon,(station_props[nearest_indx][4]).replace('  ',''),
             'K'+station_props[nearest_indx][3].replace(' ',''),station_lats[nearest_indx],
             station_lons[nearest_indx]))

########################################
# finding station data and saving it locally
########################################
#
ftp.cwd('../../data/asos-onemin/'+dirs[data_dir_indx]) # change directory back to asos-onemin
data_folder = './data/' # data where files will be saved (will be created)
if os.path.isdir(data_folder)==False:
    os.mkdir(data_folder)

sel_data_files = []
for ss in data_files:
    if ss[6:9]==station_props[nearest_indx][3].replace(' ','') and ss.endswith('.dat'):
        sel_data_files.append(ss)

for file_ii in sel_data_files:
    if os.path.isfile(data_folder+file_ii):
        continue
    with open(data_folder+file_ii, 'wb') as fp:
        ftp.retrbinary('RETR '+file_ii, fp.write) # save data files

########################################
# parsing station data and visualizing it
########################################
#
file_indx = 0
file_ii = np.sort(sel_data_files)[file_indx]
data_ii = []
with open(data_folder+file_ii, newline='') as dat_file:
    csvreader = csv.reader(dat_file)
    for row in csvreader:
        row = row[0]
        if dirs[data_dir_indx].split('-')[0]=='6405':
            data_ii.append([row[0:10],row[10:33],row[33:59],row[59:70],row[70:75],
                        row[75:80],row[80:85],row[85:90],row[90:]])
        elif dirs[data_dir_indx].split('-')[0]=='6406':
            data_ii.append([row[0:10],row[10:32],row[32:44],row[44:62],row[62:70],
                            row[70:76],row[76:86],row[86:95],row[95:99],row[99:]])

####
# the data is given in data_ii as follows (for 6405):
# row 0 - identifier for station
# row 1 - identifier + timestamp
# row 2 - visibility (N = night; D = day)
# row 3 - visibility (N = night; D = day)
# row 4 - wind direction (2-min avg)
# row 5 - wind speed     (2-min avg)
# row 6 - dir of max wind speed (5-sec)
# row 7 - speed of max wind dir (5-sec)
# row 8 - runway visual range (hundreds ft)


####
# the data is given in data_ii as follows (for 6406):
# row 0 - identifier for station
# row 1 - identifier + timestamp
# row 2 - precipitation (NP=none, S = snow, R = rain)
# row 3 - amount of precip
# row 4 - frozen precip sensor frequency
# row 5 - pressure 1
# row 6 - pressure 2
# row 7 - pressure 3
# row 8 - Avg 1min dry bulb temp
# row 9 - Avg 1min dew pt temp

########################################
# PLOTTING THE DATA
########################################
#
# Let's look at one of the pressures for a given station:
t_strs,pres,temp_dry,temp_wet = np.array([]),np.array([]),np.array([]),np.array([])
for dats in data_ii:
    try:
        t_ii = (dats[1][3:].replace(' ',''))
        pres_ii = float(dats[5])      
        temp_dry_ii = float(dats[8])
        temp_wet_ii = float(dats[9])
        t_strs = np.append(t_strs,t_ii)
        pres = np.append(pres,pres_ii)
        temp_dry = np.append(temp_dry,temp_dry_ii)
        temp_wet = np.append(temp_wet,temp_wet_ii)
    except:
        pass

t_vec = [datetime.datetime.strptime(ii[0:-4],'%Y%m%d%H%M') for ii in t_strs]

# relative humidity calculation:
# equation taken from:
# https://maxwellsci.com/print/rjaset/v6-2984-2987.pdf
#
delta_T = np.subtract(temp_dry,temp_wet) # dry - wet temps
A = 0.00066*(1.0+(0.00115*temp_wet)) # empirical relationship
P = pres*33.8639 # pressure from inHg to mb
e_w = 6.112*np.exp((17.502*temp_wet)/(240.97+temp_wet)) # sat. vapor pressure for wet-bulb temp
e_d = 6.112*np.exp((17.502*temp_dry)/(240.97+temp_dry)) # sat. vapor pressure for dry-bulb temp 
RH = ((e_w-(A*P*delta_T))/e_d)*100.0


fig,axs = plt.subplots(3,1,figsize=(10,6))

cmap = plt.cm.Set1

ax = axs[0]
ax.plot(t_vec,pres,color=cmap(0))
ax2 = axs[1]
ax2.plot(t_vec,temp_dry,color=cmap(1),label='Dry-Bulb')
ax2.plot(t_vec,temp_wet,color=cmap(2),label='Wet-Bulb')

ax3 = axs[2]
ax3.plot(t_vec,RH,color=cmap(3))

ax2.set_xlabel('Local Time',fontsize=12)
ax.set_ylabel('Pressure [inHg]',fontsize=12)
ax2.set_ylabel('Temperature [F]',fontsize=12)
ax3.set_ylabel('Humidity [%]',fontsize=14)

ax.get_yaxis().set_label_coords(-0.07,0.5)
ax2.get_yaxis().set_label_coords(-0.07,0.5)
ax3.get_yaxis().set_label_coords(-0.07,0.5)

ax.set_xticks([])
ax2.set_xticks([])
ax3.tick_params(axis='x', rotation=15)

ax2.legend()
ax.set_title('Station: {}, ({},{}) [{}]'.format(station_props[nearest_indx][3].replace(' ',''),
                                             station_props[nearest_indx][9].replace(' ',''),
                                             station_props[nearest_indx][10].replace(' ',''),
                                             station_props[nearest_indx][4].replace('  ','')))
plt.savefig(station_props[nearest_indx][3].replace(' ','')+'_test_plot.png',dpi=300,facecolor=[252.0/255.0,252.0/255.0,252.0/255.0])
plt.show()

ftp.close() # close ftp connection
