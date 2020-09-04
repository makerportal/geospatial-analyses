################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses data from the CCNY surface flux station to
# plot diurnal profiles of each flux variable
#
################################################################
#
#
import csv,datetime
import matplotlib.pyplot as plt
import numpy as np

flux_datafile = 'TOA5_10560.flux_2019_219_2000.dat' # local flux data file

#####################################
# Get flux data information
#####################################
#
data_array = [] # data array
with open(flux_datafile,'r') as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',') # reading with comma-separated values
    for row in csvreader:
        data_array.append(row) # read and save each row to data array

header1 = data_array[0] # first header
variable_names = data_array[1] # variable names are stored here
variable_units = data_array[2] # units
variable_types = data_array[3] # info about variables (averages, etc.)
data = data_array[4:] # the data values

# print('Variable List:')
# print('-'*20)
# for ii,var_ii in enumerate(variable_names):
#     print('{0:1d} - {1}'.format(ii,var_ii)) # print index of each variable
# print('-'*20)
    
#####################################
# Grab selected variables
#####################################
#
x = [datetime.datetime.strptime(ii[0],'%Y-%m-%d %H:%M:%S').hour for ii in data] # grab timestamp for plotting
var_indices = [2,36,96]
var_data_array = []
for ii,ind_ii in enumerate(var_indices):
    print('Variable 1: {0}'.format(variable_names[ind_ii]))
    var_data_array.append([float(jj[ind_ii]) for jj in data])

#####################################
# Plot selected variables
#####################################
#
plt.style.use('ggplot') # style choice for nicer plots
fig,axs = plt.subplots(2,1,figsize=(12,9)) # create figure 
ax = axs[0] # first subplot with raw data
for ii,ind_ii in enumerate(var_indices):
    ax.scatter(x,var_data_array[ii],label=variable_names[ind_ii]) # plot the variables
ax.set_xlabel('Timestamp [yyyy-mm-dd]',fontsize=16)
ax.set_ylabel('Raw Flux [W$\cdot$m$^{-2}$]',fontsize=16)
ax.legend(fontsize=16)
# second subplot with diurnal averages
ax2 = axs[1] # first subplot with raw data
for ii,ind_ii in enumerate(var_indices):
    x_avg = np.unique(x)
    y_avg = [np.nanmean(np.array(var_data_array[ii])[x==unq_x]) for unq_x in x_avg]
    ax2.plot(x_avg,y_avg,label='$\overline{'+variable_names[ind_ii]+'}$',linewidth=4.0) # plot the variables
ax2.set_xlabel('Hour of Day',fontsize=16)
ax2.set_ylabel('Mean Flux [W$\cdot$m$^{-2}$]',fontsize=16)
ax2.legend(fontsize=16)
ax.set_title('Flux Data from CCNY Tower')
fig.savefig('flux_diurnal_example.png',dpi=300,bbox_inches='tight')
plt.show()
