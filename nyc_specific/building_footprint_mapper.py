################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses the building footprint file from:
# https://data.cityofnewyork.us/Housing-Development/Building-Footprints/nqwf-w8eh
# and get information about building height and building roof
# area. It plots the geometries of each building atop a map
# of NYC
#
################################################################
#
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
import numpy as np

def basemapper():
    fig = plt.figure(figsize=(12,9)) # setup figure
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) # add subplot with projection
    ax.set_extent([bbox[0],bbox[2],bbox[1],bbox[3]], crs=ccrs.PlateCarree()) # clip map to city boundaries
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1.5, color='gray', alpha=0.5, linestyle='--') # draw gridlines
    gl.top_labels = False; gl.right_labels = False # format labels
    gl.xformatter = LONGITUDE_FORMATTER; gl.yformatter = LATITUDE_FORMATTER # format labels
    return fig,ax

def bldg_grabber():
    reader = shpreader.Reader(shpfilename) # read the shapefile with building info
    records = reader.records() # grab the records (each building)
    bldg_heights,bldg_areas,bldg_centroids,bldg_lats,bldg_lons = [],[],[],[],[]
    bldg_geoms = []
    for record in records:
        # the following IF statements handle different city footprint files with different names for heights/areas
        if 'APPROX_HGT' in list(record.attributes):
            bldg_height = record.attributes['APPROX_HGT']
            bldg_area = record.attributes['Shape__Are']
        elif 'HEIGHT' in list(record.attributes):
            bldg_height = record.attributes['HEIGHT']
            bldg_area = record.attributes['AREA']
        elif 'bldg_sq_fo' in list(record.attributes):
            bldg_height = record.attributes['no_stories']
            bldg_area = record.attributes['bldg_sq_fo']
        elif 'heightroof' in list(record.attributes):
            bldg_height = record.attributes['heightroof'] # building heights (roof height)
            bldg_area = record.attributes['shape_area'] # building area (from roof)
        if bldg_height==None or bldg_area==None:
            continue
        bldg_heights.append(bldg_height) # for analyses with anthropogenic/building energy usages
        bldg_areas.append(bldg_area) # for analyses with plan area fraction
        bldg_lons.append(record.geometry.centroid.coords[0][0]) # save center of building as coordinate
        bldg_lats.append(record.geometry.centroid.coords[0][1]) # save center of building as coordinate
        bldg_geoms.append(record.geometry) # saves geometry for plotting buildings on map
    
    print('Average Building Height: {0:2.1f} m, Area: {1:2.1f} m^2'.format(np.nanmean(bldg_heights),np.nanmean(bldg_areas)))
    return bldg_lons,bldg_lats,bldg_geoms,bldg_heights,bldg_areas
def bldg_plotter():
    fig,ax = basemapper() # create spatial map
    city_boundary_shp = ShapelyFeature(shpreader.Reader('./500Cities_City_11082016/CityBoundariescorrect_CRS_correct_CRS.shp').geometries(),
                                    ccrs.PlateCarree(), facecolor='#ECECEC',edgecolor='k') # load city boundaries
    ax.add_feature(city_boundary_shp) # add city boundary
    shape_feature = ShapelyFeature(bldg_geoms,ccrs.PlateCarree(), facecolor='k') # create building shapes
    ax.add_feature(shape_feature) # add building shapes to map
#     fig.savefig('nyc_building_footprint_financial_district.png',dpi=300,bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    shpfilename = './nyc_footprints/geo_export_ac6032f8-bdaa-4192-9feb-0918d9415df3.shp' # local building footprint file
    bldg_lons,bldg_lats,bldg_geoms,bldg_heights,bldg_areas = bldg_grabber() # grab building info from footprint shapefile
    bbox = [np.min(bldg_lons),np.min(bldg_lats),np.max(bldg_lons),np.max(bldg_lats)] # bounding box of buildings
    bldg_plotter() # plot building footprints
