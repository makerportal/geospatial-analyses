################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This codes uses a local GOES-16 file (starting with ABI-...)
# and plots the main data variable (LST in this case) on a map
# using matplotlib's 'pcolormesh()' plotter
#
################################################################
#
#
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import pyproj,datetime
#
###########################
# introductory GOES codes
###########################
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

if __name__ == '__main__':
    # below is the local GOES file in netcdf format
    sat_file = 'ABI-L2-LSTC_2020_153_17_OR_ABI-L2-LSTC-M6_G16_s20201531701133_e20201531703506_c20201531704438.nc'
    netcdf_file = Dataset(sat_file) # read netCDF file from GOES satellite
    lons,lats = lat_lon_reproj(netcdf_file) # get longitude/latitude from netcdf
    data_indx = 0 # select variable based on printed-out index (first index, 0, is usually the data)
    goes_vars = [ii for ii in netcdf_file.variables] # get variables from netcdf file
    data = data_grabber(netcdf_file) # grab the data
    bbox = [-130.2328,21.7423,-63.6722,52.8510] # bounding box for continental USA
    geo_plotter() # plot the data
