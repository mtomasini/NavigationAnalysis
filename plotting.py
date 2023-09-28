import pandas as pd
from processing import coordinate_conversion
import movingpandas
from datetime import timedelta
from holoviews import opts
import hvplot.pandas

def plot_trajectory(position_dataset, with_speed=False, seconds_binning=5):
    position_dataset['Converted Lat'] = position_dataset['Latitude'].apply(lambda x: coordinate_conversion(x))
    position_dataset['Converted Lon'] = position_dataset['Longitude'].apply(lambda x: coordinate_conversion(x))
    position_dataset['Converted Time'] = position_dataset['Time'].apply(lambda x: pd.to_datetime(x))
    
    position_stripped = position_dataset[['Converted Time', 'Converted Lat', 'Converted Lon']]
    trajectories = movingpandas.Trajectory(position_stripped, traj_id = 'logboat', t='Converted Time', x='Converted Lon', y='Converted Lat', crs="EPSG:4326")
    trajectories = movingpandas.MinTimeDeltaGeneralizer(trajectories).generalize(tolerance=timedelta(seconds=seconds_binning))
    
    opts.defaults(opts.Overlay(active_tools=['wheel_zoom'], frame_width=500, frame_height=500))
    hvplot_defaults = {'cmap':'Viridis', 'colorbar':True, 'figsize':(5,4)}
    
    if with_speed:
        plot = trajectories.to_crs({'init': 'epsg:4326'}).hvplot(title="Trajectories with current speed (m/s)", geo=True, c='speed')
    else:
        plot = trajectories.to_crs({'init': 'epsg:4326'}).hvplot(title="Trajectories", geo=True)
        
    hvplot.show(plot)