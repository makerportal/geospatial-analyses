################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses the shapefile from:
# https://github.com/makerportal/geospatial-analyses/tree/master/500cities_shapefiles
# and plots the 500 largest cities in the USA using cartopy
#
################################################################
#
#
####### import headers #######
import numpy as np
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import cartopy.feature as cfeature

def main():
    bbox = [-130.2328,21.7423,-63.6722,52.8510] # continental USA bounding box

    shapefile_loc = './500cities_shapefiles/CityBoundaries_correct_CRS.shp' # location of 500 city shapefile

    fig = plt.figure(figsize=(12,9)) # set figure size
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) # set projection and subplot
    ax.set_extent([bbox[0],bbox[2],bbox[1],bbox[3]], crs=ccrs.PlateCarree()) # set axis extents
    ax.stock_img() # add stock image with natural earth features
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none') # specify lines, resolution

    ax.add_feature(cfeature.LAND) # add land features
    ax.add_feature(cfeature.COASTLINE) # add coastline features
    ax.add_feature(states_provinces, edgecolor='gray') # add province/state features

    city_shapefiles = ShapelyFeature(shpreader.Reader(shapefile_loc).geometries(),
                                    ccrs.PlateCarree(), facecolor='r') # get the geometries of the 500 cities
    ax.add_feature(city_shapefiles) # add 500 cities shapefiles to plot
    plt.show() 
    
if __name__ == '__main__':
    main()
