################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This codes uses a local GOES-16 file (starting with ABI-...)
# and checks whether the projection is correct by printing
# out the coordinates of NYC (based on previously found indexes)
#
################################################################
#
#
import numpy as np
from netCDF4 import Dataset
import pyproj

sat_file = 'ABI-L2-LSTC_2020_153_17_OR_ABI-L2-LSTC-M6_G16_s20201531701133_e20201531703506_c20201531704438.nc'
netcdf_file = Dataset(sat_file) # read netCDF file from GOES satellite

# uncomment below to list all netCDF variables in the GOES file
# for ii in netcdf_file.variables: # list all variables from the sat file
#     print(ii)
    
h = netcdf_file.variables['goes_imager_projection'].perspective_point_height # height of satellite
r_eq = netcdf_file.variables['goes_imager_projection'].semi_major_axis # equator radius
r_pol = netcdf_file.variables['goes_imager_projection'].semi_minor_axis # polar radius
lambda_0 = netcdf_file.variables['goes_imager_projection'].longitude_of_projection_origin # longitude point of sat
lat_0 =  netcdf_file.variables['goes_imager_projection'].latitude_of_projection_origin # latitude point of sat

goes_proj = pyproj.Proj('+proj=geos +h={0:08.1f} +a= {1:08.1f} +b= {2:08.1f}'.format(h,r_eq,r_pol)+\
                        ' +lon_0={0:08.1f} +lat_0={1:08.1f} +units=m +no_defs'.format(lambda_0,lat_0)) # GOES projection
lonlat_proj = pyproj.Proj("EPSG:4326") # to lat/lon
xs = h*netcdf_file.variables['x'][:] # x-vals from GOES
ys = h*netcdf_file.variables['y'][:] # y-vals from GOES
rows,cols = np.meshgrid(xs,ys) # mesh for x/y vals
tfmr = pyproj.transformer.Transformer.from_proj(goes_proj,lonlat_proj) # the projection from GOES -> lat/lon
lats,lons = tfmr.transform(rows,cols) # lat/lon values from projection
lons[lons==np.inf] = np.nan # get rid of inf values (non-real)
lats[lats==np.inf] = np.nan # get rid of in values (non-real)
print('Are These the Correct NYC Coords? : ({0:2.5f}, {1:2.5f})'.format(lons[318,1849],lats[318,1849])) # test NYC coords
