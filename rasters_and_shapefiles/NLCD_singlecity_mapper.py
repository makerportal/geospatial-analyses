################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses the NLCD (both imperviousness and general) data 
# (https://www.mrlc.gov/data) and the 500 city shapefile to plot
# the land cover data across a given city at 30-m resolution 
# (full-res) using cartopy
#
################################################################
#
#
####### import headers #######
import os,rasterio,pyproj
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import cartopy.io.img_tiles as tiles
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import ShapelyFeature
import cartopy.feature as cfeature
#
#
##########################################
# NLCD plotter
##########################################
#
#
def main(city_shapefile,city_name):
#     nlcd_dir = '/Volumes/MacOS Ext/nlcd/imperviousness_descriptor/' # imperviousness directory
    nlcd_dir = '/Volumes/MacOS Ext/nlcd/land_cover/' # NLCD landcover directory
    nlcd_files = [ii for ii in os.listdir(nlcd_dir) if ii[0]!='.']
    nlcd_filename = [ii for ii in nlcd_files if ii.endswith('.img')][0]
    #######
    # uncomment below for NLCD land cover
    #######
    legend = np.array([0,11,12,21,22,23,24,31,41,42,43,51,52,71,72,73,74,81,82,90,95])
    leg_str = np.array(['No Data','Open Water','Perennial Ice/Snow','Developed, Open Space','Developed, Low Intensity',
           'Developed, Medium Intensity','Developed High Intensity','Barren Land (Rock/Sand/Clay)',
           'Deciduous Forest','Evergreen Forest','Mixed Forest','Dwarf Scrub','Shrub/Scrub',
           'Grassland/Herbaceous','Sedge/Herbaceous','Lichens','Moss','Pasture/Hay','Cultivated Crops',
           'Woody Wetlands','Emergent Herbaceous Wetlands'])
    #######
    # uncomment below for NLCD imperviousness
    #######
#     legend = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,127])
#     leg_str = np.array(['No Data',
#                     'Primary road in urban area : interstates and other major roads',
#                    'Primary road outside urban area : interstates and other major roads',
#                    'Secondary road in urban area : non-interstate highways',
#                    'Secondary road outside urban area : non-interstate highways',
#                    'Tertiary road in urban area : any two-lane road',
#                    'Tertiary road outside urban area : any two-lane road',
#                    'Thinned road in urban area',
#                    'Thinned road outside urban area',
#                    'Nonroad impervious surface in urban area',
#                    'Nonroad impervious surface outside urban area',
#                    'Energy production site in urban area',
#                    'Energy production site outside urban area',
#                    'NAN'])
    # colormap determination and setting bounds
    with rasterio.open(nlcd_dir+nlcd_filename) as r:
        try:
            tfm_geo_to_img = pyproj.transformer.Transformer.from_crs('epsg:4326',r.crs)
            raster_bbox_0 = [r.index(tfm_geo_to_img.transform(bbox[1],bbox[0])[0],tfm_geo_to_img.transform(bbox[1],bbox[0])[1])[0],
                             r.index(tfm_geo_to_img.transform(bbox[3],bbox[0])[0],tfm_geo_to_img.transform(bbox[3],bbox[0])[1])[0],
                            r.index(tfm_geo_to_img.transform(bbox[1],bbox[2])[0],tfm_geo_to_img.transform(bbox[1],bbox[2])[1])[0],
                             r.index(tfm_geo_to_img.transform(bbox[3],bbox[2])[0],tfm_geo_to_img.transform(bbox[3],bbox[2])[1])[0]]
            raster_bbox_1 = [r.index(tfm_geo_to_img.transform(bbox[1],bbox[0])[0],tfm_geo_to_img.transform(bbox[1],bbox[0])[1])[1],
                             r.index(tfm_geo_to_img.transform(bbox[3],bbox[0])[0],tfm_geo_to_img.transform(bbox[3],bbox[0])[1])[1],
                            r.index(tfm_geo_to_img.transform(bbox[1],bbox[2])[0],tfm_geo_to_img.transform(bbox[1],bbox[2])[1])[1],
                             r.index(tfm_geo_to_img.transform(bbox[3],bbox[2])[0],tfm_geo_to_img.transform(bbox[3],bbox[2])[1])[1]]
            raster_bbox = [int(np.min(raster_bbox_0)),int(np.min(raster_bbox_1)),int(np.max(raster_bbox_0)),int(np.max(raster_bbox_1))]
            nlcd = r.read(1, window=Window.from_slices((raster_bbox[0],raster_bbox[2]), (raster_bbox[1], raster_bbox[3])))
            nlcd = np.transpose(nlcd)
            # lat/lon delineation 

            # Or if you see an interesting feature and want to know the spatial coordinates:
            row,col = np.meshgrid(np.arange(raster_bbox[0],raster_bbox[2]),np.arange(raster_bbox[1],raster_bbox[3]))
            east, north = r.xy(row,col) # image --> spatial coordinates
            east = np.ravel(east); north = np.ravel(north)
            #         lon,lat = pyproj.transform(utm, lonlat, east, north)  
            tfm = pyproj.transformer.Transformer.from_crs(r.crs,'epsg:4326')
            lat,lon = tfm.transform(east,north)
            lons = np.reshape(lon,np.shape(row))
            lats = np.reshape(lat,np.shape(col))

            # colormap determination and setting bounds
            cmap_in = r.colormap(1) # get colormap information
            cmap_in = [[np.float(jj)/255.0 for jj in cmap_in[ii]] for ii in cmap_in] # format colormap for matplotlib
            indx_list = np.unique(nlcd) # find unique NLCD values in image
            r_cmap = []    
            for ii in legend:
                r_cmap.append(cmap_in[ii])
            r_cmap[0] = [0.0,0.0,0.0,1.0]
            raster_cmap = ListedColormap(r_cmap) # defining the NLCD specific color map
            norm = mpl.colors.BoundaryNorm(legend, raster_cmap.N) # specifying colors based on num. unique points
        except:
            print('FAILURE') # if there's an issue, print 'FAILURE'

    fig = plt.figure(figsize=(14,14)) # figure sizing
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) # add axis with projection 

    # This loop is for creation of a legend below the map
    custom_lines,custom_colors,custom_strs = [],[],[]
    for qq in indx_list:
        if qq in legend:
            legend_loc = np.where(qq==legend)[0][0]
            custom_lines.append(plt.Line2D([0],[0], marker='s',color=raster_cmap(legend_loc), markersize=12,linestyle=''))
            custom_colors.append(raster_cmap(legend_loc)) # legend colors
            custom_strs.append(leg_str[legend_loc]) # legend strings
            
    custom_lines.append(plt.Line2D([0],[0], marker='s',color='w', markersize=12,linestyle=''))
    custom_colors.append('w') # legend colors
    custom_strs.append('City Boundary') # legend strings

    ax.set_axis_off() # turn off the frame
    ax.set_title(city_name.title(),fontsize=16) # city name in the title
    
    # Limit the extent of the map to a small longitude/latitude range.
    ax.set_extent([bbox[0],bbox[2],bbox[1],bbox[3]], crs=ccrs.PlateCarree())
    # format the gridlines and lat/lon coordinate text
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='#EBEBEB', alpha=0.5, linestyle='--')
    gl.label_style = {'size': 25}
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    
#     nlcd = np.ma.masked_where(nlcd==0,nlcd) # the black 'no data' values can be masked, if desired (looks better)

    ax.add_feature(city_shapefile) # add chosen city shapefile boundary to the plot
    ax.pcolormesh(lons,lats,nlcd, norm=norm,
                 alpha=0.6,cmap=raster_cmap) # plotting actual NLCD data

    ax2 = fig.add_subplot(414) # subplot for legend
    ax2.set_axis_off() # turn off legend frame
    leg_plt_save = ax2.legend(custom_lines, custom_strs,fontsize=12,ncol=2,loc='center')
    leg_plt_save.get_frame().set_facecolor('#EBEBEB') # color for legend
    leg_plt_save.set_bbox_to_anchor((0.48,-0.6)) # legend bbox

def city_shapefile_mapper():
    city_sel = input('Please Enter a City: ') # city to plot
    shapefile_loc = '../500cities_shapefiles/CityBoundaries_correct_CRS.shp' # location of 500 city shapefile
    city_names = [ii.attributes['NAME'].lower() for ii in shpreader.Reader(shapefile_loc).records()] # 500 city names
    
    city_indx = [ii for ii in range(0,len(city_names)) if city_sel==city_names[ii]] # find shapefile index from 500 cities

    if len(city_indx)==0: 
        print('No City at that Name') # let user know that there is no city at that name
        return
    else:
        city_indx = city_indx[0] # select index of city shapefile

    zoom = 0.1
    city_geom = [ii.geometry for ii in shpreader.Reader(shapefile_loc).records()][city_indx] # grab the city shapefile
    bbox = [city_geom.bounds[0]-zoom,city_geom.bounds[1]-zoom,
            city_geom.bounds[2]+zoom,city_geom.bounds[3]+zoom] # bbox from city boundary

    if city_geom.type!='MultiPolygon':
        city_geom = [city_geom] # this is a requirement for plotting features
        
    city_shapefile = ShapelyFeature(city_geom,ccrs.PlateCarree(), facecolor=[0.0,0.0,0.0,0.0],
                                    edgecolor='#ECECEC',linewidth=5.0) # get the geometries of the 500 cities
    return bbox,city_shapefile,city_names[city_indx]
    
if __name__ == '__main__':
    bbox,city_shapefile,city_name = city_shapefile_mapper()
    main(city_shapefile,city_name)
