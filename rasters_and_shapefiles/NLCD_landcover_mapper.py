################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses the NLCD land cover data from:
# https://www.mrlc.gov/data
# and plots the land cover information using cartopy
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

bbox = [-130.2328,21.7423,-63.6722,52.8510] # bounding box for continental USA

#
#
##########################################
# NLCD plotter
##########################################
#
#
def main():
    nlcd_dir = '/Volumes/MacOS Ext/nlcd/land_cover/' # local directory where NLCD folder is located
    nlcd_files = [ii for ii in os.listdir(nlcd_dir) if ii[0]!='.']
    nlcd_filename = [ii for ii in nlcd_files if ii.endswith('.img')][0]
    legend = np.array([0,11,12,21,22,23,24,31,41,42,43,51,52,71,72,73,74,81,82,90,95])
    leg_str = np.array(['No Data','Open Water','Perennial Ice/Snow','Developed, Open Space','Developed, Low Intensity',
           'Developed, Medium Intensity','Developed High Intensity','Barren Land (Rock/Sand/Clay)',
           'Deciduous Forest','Evergreen Forest','Mixed Forest','Dwarf Scrub','Shrub/Scrub',
           'Grassland/Herbaceous','Sedge/Herbaceous','Lichens','Moss','Pasture/Hay','Cultivated Crops',
           'Woody Wetlands','Emergent Herbaceous Wetlands'])
    # colormap determination and setting bounds
    with rasterio.open(nlcd_dir+nlcd_filename) as r:
        try:
            oviews = r.overviews(1) # list of overviews from biggest to smallest
            oview = oviews[6] # we grab a smaller view, since we're plotting the entire USA
            print('Decimation factor= {}'.format(oview))
            # NOTE this is using a 'decimated read' (http://rasterio.readthedocs.io/en/latest/topics/resampling.html)
            nlcd = r.read(1, out_shape=(1, int(r.height // oview), int(r.width // oview)))

            # Or if you see an interesting feature and want to know the spatial coordinates:
            row,col = np.meshgrid(np.arange(0,r.height-(oview),oview),np.arange(0,r.width-oview,oview))
            east, north = r.xy(row,col) # image --> spatial coordinates
            east = np.ravel(east); north = np.ravel(north) # collapse coordinates for efficient transformation

            tfm = pyproj.transformer.Transformer.from_crs(r.crs,'epsg:4326') # transform for raster image coords to lat/lon
            lat,lon = tfm.transform(east,north) # transform the image coordinates
            lons = np.reshape(lon,np.shape(row)) # reshape to grid
            lats = np.reshape(lat,np.shape(col)) # reshape to grid

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

    fig = plt.figure(figsize=(12,8)) # figure sizing
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree()) # add axis with projection 

    # This loop is for creation of a legend below the map
    custom_lines,custom_colors,custom_strs = [],[],[]
    for qq in indx_list:
        if qq in legend:
            legend_loc = np.where(qq==legend)[0][0]
            custom_lines.append(plt.Line2D([0],[0], marker='s',color=raster_cmap(legend_loc), markersize=12,linestyle=''))
            custom_colors.append(raster_cmap(legend_loc)) # legend colors
            custom_strs.append(leg_str[legend_loc]) # legend strings

    ax.set_axis_off() # turn off the frame

    # Limit the extent of the map to a small longitude/latitude range.
    ax.set_extent([bbox[0],bbox[2],bbox[1],bbox[3]], crs=ccrs.PlateCarree())

    # nlcd = np.ma.masked_where(nlcd==127,nlcd) # the gray 'no data' values can be masked, if desired (looks better)

    ax.pcolormesh(lons,lats,np.transpose(nlcd), norm=norm,
                 alpha=0.6,cmap=raster_cmap) # plotting actual NLCD data

    ax2 = fig.add_subplot(414) # subplot for legend
    ax2.set_axis_off() # turn off legend frame
    leg_plt_save = ax2.legend(custom_lines, custom_strs,fontsize=12,ncol=2,loc='center')
    leg_plt_save.get_frame().set_facecolor('#ebebeb') # color for legend
    leg_plt_save.set_bbox_to_anchor((0.48,-0.6)) # legend bbox

if __name__ == '__main__':
    main()
