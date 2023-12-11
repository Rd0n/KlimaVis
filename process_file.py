import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import os

from cartopy.util import add_cyclic_point
from video import make_video


def proc_file(file_name, proc_type='absolute', min=None, max=None, comp=None, steps=None):
    log('Processing file ' + file_name + '...')
    # Load NetCDF file
    data = nc.Dataset(file_name)

    # Create folder for images
    if file_name.find('/') == -1:
        short_name = file_name.split('.')[0]
    else:
        short_name = file_name.split('/')[len(file_name.split('/')) - 1].split('.')[0]
    out_folder = os.path.join('images', short_name)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    log('File loaded', short_name)

    # Get timesteps, longitude and latitude
    if steps is None:
        steps = len(data.variables['time'])
    longitude = data.variables['lon']
    latitude = data.variables['lat']

    # Get minimum and maximum near-surface temperature in Celsius of the first timestep and use +-10 as range
    if min is not None and max is not None:
        tas_vmin = min
        tas_vmax = max

    elif proc_type == 'relative':
        tas_vmin, tas_vmax = calc_anomaly(file_name, file_name)

    else:
        tas_vmin = np.min(data.variables['tas'][0]) - 273.15
        tas_vmax = np.max(data.variables['tas'][0]) - 273.15

    # Specify levels to ensure consistency across all frames (consistent colorbar)
    levels = np.linspace(tas_vmin, tas_vmax, 200)  # 50 different colors
    log('Temperature range: ' + str(tas_vmin) + ' to ' + str(tas_vmax) + ' degrees Celsius', short_name)

    log('Calculating frames...', short_name)
    # Create frame for every timestep and save the png
    for i in range(steps):
        # Get temperature of i-th timestep and project it on flat world map
        if proc_type == 'relative':
            tas = data.variables['tas'][i] - data.variables['tas'][0]
        if proc_type == 'relative_to':
            data2 = nc.Dataset('data/tas_yearly/' + comp + '.nc')
            tas = data.variables['tas'][i] - data2.variables['tas'][0]
        else:
            tas = data.variables['tas'][i] - 273.15  # Kelvin to Celsius
        projection = ccrs.PlateCarree()  # Flat world map

        # Add cyclic point to avoid white line at 0 degree longitude
        cyclic_data, cyclic_lons = add_cyclic_point(tas, coord=longitude)

        # Create filled contour plot
        fig, ax = plt.subplots(subplot_kw={'projection': projection})
        lon, lat = np.meshgrid(cyclic_lons, latitude)
        contour = ax.contourf(lon, lat, cyclic_data, cmap='coolwarm', transform=projection, vmin=tas_vmin,
                              vmax=tas_vmax, levels=levels)

        # remove black borders of projection

        # Add coastlines
        ax.coastlines(alpha=0.5, lw=0.3)

        # Add padding to index
        index = str(i)
        while len(index) < 3:
            index = '0' + index


        # Save frame as png whthout borders
        plt.savefig(out_folder + '/tas-' + index + '.png', bbox_inches='tight', pad_inches=0, dpi=1000)
        plt.close()
        log('Frame ' + str(i + 1) + ' of ' + str(steps) + ' done', short_name)

    log('Frames created', short_name)

    # Create video
    make_video(short_name, out_folder)

    return


def calc_anomaly(base_file, comp_file):
    # Load NetCDF files
    base_data = nc.Dataset(base_file)
    comp_data = nc.Dataset(comp_file)

    # Get timesteps
    steps = len(comp_data.variables['time'])

    tas_vmin = 0
    tas_vmax = 0

    for i in range(steps):
        # Get temperature of i-th timestep and project it on flat world map
        tas_scale = comp_data.variables['tas'][i] - base_data.variables['tas'][0]

        if tas_vmin > np.min(tas_scale):
            tas_vmin = np.min(tas_scale)

        if tas_vmax < np.max(tas_scale):
            tas_vmax = np.max(tas_scale)

    log(str(tas_vmin) + ", " + str(tas_vmax), base_file.split('/')[len(base_file.split('/')) - 1].split('.')[0])
    return tas_vmin, tas_vmax


def log(msg, level='INFO'):
    print('[' + level + '] ' + msg)
    return
