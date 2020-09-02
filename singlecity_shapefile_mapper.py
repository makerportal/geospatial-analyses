################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses the shapefile from:
# https://github.com/makerportal/geospatial-analyses/tree/master/500cities_shapefiles
# and plots a single city selected by the user using cartopy
#
################################################################
#
#
####### import headers #######
import numpy as np
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.crs as ccrs
from cartopy.feature import ShapelyFeature
import cartopy.feature as cfeature

def main():
    city_sel = 'chicago' # city to plot
    shapefile_loc = './500cities_shapefiles/CityBoundaries_correct_CRS.shp' # location of 500 city shapefile
    city_names = [ii.attributes['NAME'].lower() for ii in shpreader.Reader(shapefile_loc).records()] # 500 city names

    city_indx = [ii for ii in range(0,len(city_names)) if city_sel==city_names[ii]] # find shapefile index from 500 cities

    if len(city_indx)==0: 
        print('No City at that Name') # let user know that there is no city at that name
        return
    else:
        city_indx = city_indx[0] # select index of city shapefile

    zoom = 0.1
    city_geom = [ii.geometry for ii in shpreader.Reader(shapefile_loc).records()][city_indx] # grab the city shapefile
    bbox = [city_geom.bounds[0]-zoom,city_geom.bounds[1]-zoom,city_geom.bounds[2]+zoom,city_geom.bounds[3]+zoom] # bbox from city boundary

    fig = plt.figure(figsize=(12,9)) # set figure size
    ax = fig.add_subplot(projection=ccrs.PlateCarree()) # set projection and subplot
    ax.set_extent([bbox[0],bbox[2],bbox[1],bbox[3]], crs=ccrs.PlateCarree()) # set axis extents
    ax.stock_img() # add stock image with natural earth features
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='10m',
        facecolor='none') # specify lines, resolution

    ax.add_feature(cfeature.LAND) # add land features
    ax.add_feature(cfeature.COASTLINE) # add coastline features
    ax.add_feature(states_provinces, edgecolor='gray') # add province/state features

    if city_geom.type!='MultiPolygon':
        city_geom = [city_geom]
        
    city_shapefiles = ShapelyFeature(city_geom,ccrs.PlateCarree(), facecolor='#3b3b3b') # get the geometries of the 500 cities
    ax.add_feature(city_shapefiles) # add 500 cities shapefiles to plot
    ax.set_title(city_names[city_indx].title(),fontsize=16) # set title
    plt.show() 
    
if __name__ == '__main__':
    main()
