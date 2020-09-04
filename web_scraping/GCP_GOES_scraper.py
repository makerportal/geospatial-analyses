################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code grabs data from the Google Cloud Platform (GCP)
# repository where GOES-16/17 data files are stored in netCDF
# format. It saves files at a given time to the local folder
# and then plots it using 'pcolormesh' atop a map of USA
#
################################################################
#
#
from google.cloud import storage
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import os,pyproj,datetime
import numpy as np

##############################
# Establishing GCP Connection
##############################
#
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GOOGLE_AUTH_CREDS_CUERG.json" # local google auth credentials
client = storage.Client() # start the storage client
bucket_16 = client.get_bucket('gcp-public-data-goes-16') # call the GOES-16/17 storage bucket

#########################
# satellite functions 
#########################
#
def lat_lon_reproj(netcdf_file):
    # list all netCDF variables in the GOES file
    print('Data Indices:')
    for ii,dats in enumerate(netcdf_file.variables): # list all variables from the sat file
        print('{0:1d} - {1}'.format(ii,dats))

    h = netcdf_file.variables['goes_imager_projection'].perspective_point_height # height of satellite
    r_eq = netcdf_file.variables['goes_imager_projection'].semi_major_axis # equator radius
    r_pol = netcdf_file.variables['goes_imager_projection'].semi_minor_axis # polar radius
    lambda_0 = netcdf_file.variables['goes_imager_projection'].longitude_of_projection_origin # longitude point of sat
    lat_0 =  netcdf_file.variables['goes_imager_projection'].latitude_of_projection_origin # latitude point of sat

    goes_proj = pyproj.Proj('+proj=geos +h={0:08.1f} +a= {1:08.1f} +b= {2:08.1f}'.format(h,r_eq,r_pol)+\
                            ' +lon_0={0:08.1f} +lat_0={1:08.1f} +units=m sweep=x +no_defs'.format(lambda_0,lat_0)) # GOES projection
    lonlat_proj = pyproj.Proj("EPSG:4326") # to lat/lon
    xs = h*netcdf_file.variables['x'][:] # x-vals from GOES
    ys = h*netcdf_file.variables['y'][:] # y-vals from GOES
    rows,cols = np.meshgrid(xs,ys) # mesh for x/y vals
    tfmr = pyproj.transformer.Transformer.from_proj(goes_proj,lonlat_proj) # the projection from GOES -> lat/lon
    lats,lons = tfmr.transform(rows,cols) # lat/lon values from projection
    lons[lons==np.inf] = 0.0 # must remove infinite values for plotting, otherwise an error is raised
    lats[lats==np.inf] = 0.0 # must remove infinite values for plotting, otherwise an error is raised
    return lons,lats
#
###########################
# Grabbing actual data
###########################
#
def data_grabber(netcdf_file):
    print('Data Variable: {0} [{1}] ({2})'.format(goes_vars[data_indx],
                                                  netcdf_file.variables[goes_vars[data_indx]].units,
                                                  netcdf_file.variables[goes_vars[data_indx]].long_name)) # print info
    data = (netcdf_file.variables[goes_vars[data_indx]])[:] # this grabs the data, which is a masked array
    return data

#
###########################
# Plotting the actual data
###########################
#
def geo_plotter():
    fig = plt.figure(figsize=(14,12))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) # add projected subplot
    ax.set_extent([bbox[0],bbox[2],bbox[1],bbox[3]], crs=ccrs.PlateCarree()) # set extents
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='10m',
        facecolor='None') # specify lines, resolution for USA and states

    ax.add_feature(cfeature.LAND,facecolor='#ECECEC') # add land features
    ax.add_feature(cfeature.COASTLINE) # add coastline features
    ax.add_feature(states_provinces, edgecolor='k') # add province/state features
    # format the gridlines and lat/lon coordinate text
    # gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
    #               linewidth=2, color='#3b3b3b', alpha=0.3, linestyle='--')
    # gl.label_style = {'size': 12}
    # gl.top_labels = False
    # gl.right_labels = False
    # gl.xformatter = LONGITUDE_FORMATTER
    # gl.yformatter = LATITUDE_FORMATTER
    ax.set_axis_off() # turn off the frame
    p1 = ax.pcolormesh(lons,lats,data,transform=ccrs.PlateCarree()) # PLOT DATA - this plots the data with colormap
    cbar = fig.colorbar(p1,fraction=0.025, pad=0.04)
    cbar.ax.set_ylabel('{0} [{1}]'.format(goes_vars[data_indx],
                                          netcdf_file.variables[goes_vars[data_indx]].units),fontsize=16)
    time_bounds = [netcdf_file.time_coverage_start,netcdf_file.time_coverage_end]
    ax.set_title('{0} on {1} from {2} - {3}'.format(netcdf_file.variables[goes_vars[data_indx]].long_name,
                                           time_bounds[0].split('T')[0],
                                                   time_bounds[0].split('T')[1],
                                                   time_bounds[1].split('T')[1]),fontsize=16)
#     fig.savefig('GOES16_LST_test.png',dpi=300,bbox_inches='tight') # uncomment to save locally
    plt.show()
    return

##############################
# Picking file based on date
# of interest, and saving it
# locally
##############################
#
def GCP_data_scraper():
    yr = '{:0004d}'.format(t_search.year) # formats the year for GCP
    yday = '{:003d}'.format(t_search.timetuple().tm_yday) # formats the julian day (year day) for GCP
    thour = '{:02d}'.format(t_search.hour) # formats the hour for GCP

    prefix_16 = product_ID+yr+'/'+yday+'/'+thour # this is the relative folder where the GOES-16 data will be
    blobs_16 = bucket_16.list_blobs(prefix=prefix_16) # get all files in prefix

    print('Files in this repository:')
    goes_files = []
    for blob in blobs_16:
        print(blob.name) # these are the files that will be downloaded locally
        goes_files.append(blob)

    selected_file = goes_files[0] # select the first file in the folder
    selected_filename = goes_folder_local+selected_file.name.split('/')[-1]
    if os.path.isfile(selected_filename): 
        pass # don't re-download the file if it already exists
    else:
        # download the file to the local GOES-16 repository
        selected_file.download_to_filename(selected_filename)
    return selected_filename
   
if __name__ == '__main__':
    goes_folder_local = '' # local repository where LST files will be stored
    prod = 'LST' # select product
    product_ID = 'ABI-L2-'+prod+'C/' # ABI, L2 product identifier, CONUS
    t_search = datetime.datetime(2020,7,1,17) # datetime of desired data file
    selected_filename = GCP_data_scraper() # this grabs the data from the Google cloud server
    netcdf_file = Dataset(selected_filename) # read netCDF file from GOES satellite
    lons,lats = lat_lon_reproj(netcdf_file) # get longitude/latitude from netcdf
    data_indx = 0 # select variable based on printed-out index (first index, 0, is usually the data)
    goes_vars = [ii for ii in netcdf_file.variables] # get variables from netcdf file
    data = data_grabber(netcdf_file) # grab the data
    bbox = [-130.2328,21.7423,-63.6722,52.8510] # bounding box for continental USA
    geo_plotter() # plot the data
