################################################################
# Copyright (c) 2020 
# Author: Joshua Hrisko
################################################################
#
# This code uses data from the CCNY surface flux station to
# investigate and plot the data from the station
#
################################################################
#
#
import csv,datetime
import matplotlib.pyplot as plt

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

print('Variable List:')
print('-'*20)
for ii,var_ii in enumerate(variable_names):
    print('{0:1d} - {1}'.format(ii,var_ii)) # print index of each variable
print('-'*20)
    
#####################################
# Grab selected variables
#####################################
#
x = [datetime.datetime.strptime(ii[0],'%Y-%m-%d %H:%M:%S') for ii in data] # grab timestamp for plotting
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
fig,ax = plt.subplots(figsize=(12,9)) # create figure 
for ii,ind_ii in enumerate(var_indices):
    ax.plot(x,var_data_array[ii],label=variable_names[ind_ii]) # plot the variables
ax.set_xlabel('Timestamp [yyyy-mm-dd]',fontsize=16)
ax.set_ylabel('Flux [W$\cdot$m$^{-2}$]',fontsize=16)
ax.legend(fontsize=16)
plt.show()
