# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:20:28 2020

@author: at18707
"""

"""
Created on Thu Apr 16 12:57:08 2020

@author: Erin Walker

Last Updated: 03/11/2020

Script that produces Figure 3 from 'The numerous approaches to
tracking extratropical cyclones
and the challenges they present' Accepted in Weather Sept 2020.

"""

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset as ncfile
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib
import os
import pandas as pd

##################################################
##                  NHC                         ##
##################################################

### Ophelia ###

dfophelia = pd.read_csv("input/NHC_Ophelia_best_track_2017.csv",skiprows=2, names = ['Date/Time','Lat','Lon','Pressure','Wind Speed (kt)', 'Hurricane Category'])

dti = pd.date_range('2017-10-09', '2017-10-17 18:00:00', freq='6H')
dti_new = dti.tz_localize('UTC')
dfophelia['Date'] = dti_new
dfophelia['Lat'] = pd.to_numeric(dfophelia['Lat'])
nhc_track_ophelia = dfophelia[['Date','Lat','Lon','Pressure']]
nhc_track_ophelia['Lon'][34] = '1.5'
nhc_track_ophelia['Lon'][35] = '5.3'
nhc_track_ophelia['Lon'] = pd.to_numeric(nhc_track_ophelia['Lon'])
nhc_track_ophelia['Lon'][:34] = -nhc_track_ophelia['Lon'][:34]

### Oscar ###

dfoscar = pd.read_csv("input/NHC_Oscar_best_track_2018.csv")

##Change date and time into readable
dti = pd.date_range('2018-10-26 18:00:00', '2018-11-04 12:00:00', freq='6H')
dti_new = dti.tz_localize('UTC')
dfoscar['Date'] = dti_new
#Change Lat and lon into numerics
lat = dfoscar['Lat'].str[:-1]
lon = dfoscar['Lon'].str[:-1]
dfoscar['Lat'] = lat
dfoscar['Lat'] = pd.to_numeric(dfoscar['Lat'])
dfoscar['Lon'] = lon
dfoscar['Lon'] = pd.to_numeric(dfoscar['Lon'])
dfoscar['Lon'] = -dfoscar['Lon']
nhc_track_oscar = dfoscar[['Date','Lat','Lon','Intensity (mb)']]


##########################################################################
##                            MCMS open                                 ##
##########################################################################

### Ophelia ###
df2_ophelia = pd.read_csv("input/MERRA_Ophelia_track_2017.csv",skiprows=2, names = ['Date','Time','Lat','Lon','Pressure'])

dti2_ophelia = pd.date_range('2017-10-14 18:00:00', '2017-10-18 00:00:00', freq='6H')
dti_new2_ophelia = dti2_ophelia.tz_localize('UTC')
df2_ophelia['Date'] = dti_new2_ophelia

#Change Lat and lon into numerics
df2_ophelia['Lat'] = pd.to_numeric(df2_ophelia['Lat'])
df2_ophelia['Lon'] = pd.to_numeric(df2_ophelia['Lon'])

mcms_track_ophelia = df2_ophelia[['Date','Lat','Lon','Pressure']]


### Oscar ###

df2_oscar = pd.read_csv("input/MERRA_Oscar_track_2018.csv",skiprows=2, names = ['Date','Time','Lat','Lon','Pressure'])

##Change date and time into readable
dti2_oscar = pd.date_range('2018-10-25 12:00:00', '2018-11-04 18:00:00', freq='6H')
dti_new2_oscar = dti2_oscar.tz_localize('UTC')
df2_oscar['Date'] = dti_new2_oscar

df2_oscar['Lat'] = pd.to_numeric(df2_oscar['Lat'])
df2_oscar['Lon'] = pd.to_numeric(df2_oscar['Lon'])

mcms_track_oscar = df2_oscar[['Date','Lat','Lon','Pressure']]

###########################################################################
##                       MASSEY    OPHELIA                               ##
###########################################################################

fname = "input/era5_oct_2017_6hrly_mslp_L5_E4_S3_48hrs_NA-UK.txt"
trk_no = "1366"

# read mslp data
nlist = fname.split("/")[1].split("_")
nc = ncfile(os.path.relpath("data/era5/"+("_").join(nlist[:-5])+".nc"))
pname = ("_").join([nlist[0],nlist[1],nlist[5],nlist[6]]) #,nlist[6]])
mslp = nc.variables['item16222_1hrly_mean'][:].squeeze()       # item16222_6hrly_inst | SLP
lat = nc.variables['latitude'][:]                  # latitude0 | lat, need flip() if latter
lon = nc.variables['longitude'][:]# % 360            # longitude0 | lon, need % 360 if latter

mslp, lon = shiftgrid(180.0, mslp,lon,start=False)

# set up map projection
LON,LAT=np.meshgrid(lon,lat)
m = Basemap(projection='cyl',llcrnrlat=30,urcrnrlat=65,llcrnrlon=-30,urcrnrlon=10,resolution='i')    # region same as that defined in load_and_print_track.py
# convert lats and lons to map projection coords
x, y =m(LON,LAT)

# plot setup
cmap = matplotlib.cm.get_cmap('coolwarm')
levels = np.arange(22)*2.5 +980
fig = plt.figure(figsize=[10,10])
nrow = 4
ncol = 4

# read track data
with open(os.path.relpath(fname)) as fh:
    lines = [line.strip("\t").rstrip("\n") for line in fh]
trk_idx = lines.index("Trk: "+trk_no)
trk_np = int(lines[trk_idx+1].strip("np: "))
# flag error if more time steps than frames
if (trk_np > nrow*ncol):
    print("CAUTION: There are more time steps than plotting frames!")

# do the plotting
ts = np.zeros((trk_np), dtype=int)
lon = np.zeros((trk_np))
lat = np.zeros((trk_np))
intensity = np.zeros((trk_np))


label_added= False


fig,ax1 = plt.subplots(1,2, figsize=(10,10))
m = Basemap(projection='cyl',llcrnrlat=10,urcrnrlat=70,llcrnrlon=-70,urcrnrlon=10,resolution='i',ax=ax1[0])    # region same as that defined in load_and_print_track.py

for l in range(trk_idx+2, trk_idx+2+min(trk_np,nrow*ncol)):
    info = lines[l].split()
    ts[l-(trk_idx+2)] = int(info[0])
    lon[l-(trk_idx+2)] = float(info[1])
    lat[l-(trk_idx+2)] = float(info[2])
    intensity[l-(trk_idx+2)] = float(info[4])
    
    if (lon[l-(trk_idx+2)]>= 180):
            lon[l-(trk_idx+2)]= lon[l-(trk_idx+2)]-360
     
    
    # this time step
    ax1[0].plot(lon[l-(trk_idx+2)], lat[l-(trk_idx+2)], 'x', markersize=5, mew=3, c='k', label='Massey')

    im= ax1[0].contourf(x,y,mslp[ts[l-(trk_idx+9)],:,:]/100.,extend="both",levels=levels, cmap = cmap)   
    
    # previous time steps, if any
    if ((l-(trk_idx+2)) > 0):
        for nt in range(1, (l-(trk_idx+2)+1))[::-1]:
            if (intensity[l-(trk_idx+2)] <= 97500):
                ax1[0].annotate("16.10. 06UTC", xy=(-11,50),xycoords='data', xytext =(-100,20),textcoords='offset points', arrowprops=dict(arrowstyle="->"))
             
            else:
                ax1[0].plot(lon[l-nt-(trk_idx+2)], lat[l-nt-(trk_idx+2)], '-', markersize=3.5, mew=1, c='k')
                ax1[0].plot([lon[l-nt-(trk_idx+2)], lon[l-nt-(trk_idx+2)+1]], [lat[l-nt-(trk_idx+2)], lat[l-nt-(trk_idx+2)+1]],c='k',mew=1)
    
    
    ax1[0].plot(nhc_track_ophelia.Lon, nhc_track_ophelia.Lat, marker ='o',c='r',markersize=5,label='NHC Best Track')
    ax1[0].plot(mcms_track_ophelia.Lon, mcms_track_ophelia.Lat, marker ='^',markersize=5,c='#1f77b4',label='MCMS')
   
    m.drawcoastlines(color='grey')
    m.drawparallels(np.arange(-90.,120.,15.),'grey',labels=[1,0,0,0],textcolor='black')
    m.drawmeridians(np.arange(-180.,180.,10.),'grey',labels=[0,0,0,1],textcolor='black')

label = 'a)'
ax1[0].set_title('Ophelia, 2017',size=14)
ax1[0].text(0,1.02,label,fontsize=14,transform=ax1[0].transAxes,va="bottom", ha="left")


###########################################################################
##                       MASSEY    OSCAR                                 ##
###########################################################################

fname = "input/era5_mslp_2018-2019_ondjfm_6hrly_L5_E4_S3_48hrs_NH-NH.txt"
trk_no = "2501"

nlist = fname.split("\\")[7].split("_")
nc = ncfile(os.path.relpath("data/era5/"+("_").join(nlist[:-5])+".nc"))
pname = ("_").join([nlist[0],nlist[1],nlist[5],nlist[6]]) #,nlist[6]])
mslp = nc.variables['MSL'][:].squeeze()       # item16222_6hrly_inst | SLP
lat = nc.variables['lat'][:]                  # latitude0 | lat, need flip() if latter
lon = nc.variables['lon'][:]# % 360            # longitude0 | lon, need % 360 if latter

mslp, lon = shiftgrid(180.0, mslp,lon,start=False)
LON,LAT=np.meshgrid(lon,lat)

cmap = matplotlib.cm.get_cmap('coolwarm')
levels = np.arange(22)*2.5 +980
nrow = 8
ncol = 8

# read track data
with open(os.path.relpath(fname)) as fh:
    lines = [line.strip("\t").rstrip("\n") for line in fh]
trk_idx = lines.index("Trk: "+trk_no)
trk_np = int(lines[trk_idx+1].strip("np: "))
# flag error if more time steps than frames
if (trk_np > nrow*ncol):
    print("CAUTION: There are more time steps than plotting frames!")

# do the plotting
ts = np.zeros((trk_np), dtype=int)
lon = np.zeros((trk_np))
lat = np.zeros((trk_np))
intensity = np.zeros((trk_np))

label_added= False

m = Basemap(projection='cyl',llcrnrlat=10,urcrnrlat=70,llcrnrlon=-70,urcrnrlon=10,ax=ax1[1], resolution='i')    # region same as that defined in load_and_print_track.py

x, y =m(LON,LAT)

for l in range(trk_idx+2, trk_idx+2+min(trk_np,nrow*ncol)):
    info = lines[l].split()
    ts[l-(trk_idx+2)] = int(info[0])
    lon[l-(trk_idx+2)] = float(info[1])
    lat[l-(trk_idx+2)] = float(info[2])
    intensity[l-(trk_idx+2)] = float(info[4])
    
    if (lon[l-(trk_idx+2)]>= 180):
            lon[l-(trk_idx+2)]= lon[l-(trk_idx+2)]-360
     

    # this time step
    ax1[1].plot(nhc_track_oscar.Lon, nhc_track_oscar.Lat, marker ='o',markersize=5,c='r',label='NHC Best Track')
    ax1[1].plot(mcms_track_oscar.Lon, mcms_track_oscar.Lat, marker ='^',markersize=5,c='#1f77b4',label='MCMS')
    ax1[1].plot(lon[l-(trk_idx+2)], lat[l-(trk_idx+2)], 'x', markersize=5, mew=3, c='k', label='Massey')
    
    im= ax1[1].contourf(x,y,mslp[ts[l-(trk_idx+5)],:,:]/100.,extend="both",levels=levels, cmap = cmap)   
    # previous time steps, if any
    if ((l-(trk_idx+2)) > 0):
        for nt in range(1, (l-(trk_idx+2)+1))[::-1]:
            if (intensity[l-(trk_idx+2)] <= 96800) and (intensity[l-(trk_idx+2)] >= 96700) :
                ax1[1].annotate("03.11. 18UTC", xy=(-17,57),xycoords='data', xytext =(0,-50),textcoords='offset points', arrowprops=dict(arrowstyle="->"))
 
            else:
                ax1[1].plot(lon[l-nt-(trk_idx+2)], lat[l-nt-(trk_idx+2)], '-', markersize=3.5, mew=1, c='k')
                ax1[1].plot([lon[l-nt-(trk_idx+2)], lon[l-nt-(trk_idx+2)+1]], [lat[l-nt-(trk_idx+2)], lat[l-nt-(trk_idx+2)+1]],c='k',mew=1)
    
    
    m.drawcoastlines(color='grey')
    m.drawparallels(np.arange(-90.,120.,15.),'grey',labels=[0,0,0,0])
    m.drawmeridians(np.arange(-180.,180.,10.),'grey',labels=[0,0,0,1],textcolor='black')


handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax1[0].legend(by_label.values(), by_label.keys(),loc='lower right')

label = 'b)'

ax1[1].set_title('Oscar, 2018',size=14)
ax1[1].text(0.04,1.07,label,transform=ax1[1].transAxes,fontsize=14,va="top",ha="right")

fig.colorbar(im,ax=[ax1[0:]],location='bottom',shrink=0.6,label='mean sea level pressure, hPa')

plt.savefig('ophelia_and_oscar_storm_tracking.pdf' ,dpi=600)

plt.show()