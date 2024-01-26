import sys

import pandas as pd
# import geopandas as gpd
import movingpandas as mpd
# import shapely as shp

import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from holoviews import opts

from processing import concatenate_datasets, coordinate_conversion
from plotting import cut_transect, plot_trajectory, calculate_mean_speed_through_water, calculate_bearing, calculate_winds

plot_defaults = {'linewidth':5, 'capstyle':'round', 'figsize':(9,3), 'legend':True}
opts.defaults(opts.Overlay(active_tools=['wheel_zoom'], frame_width=500, frame_height=500))
hvplot_defaults = {'cmap':'Viridis', 'colorbar':True, 'figsize':(5,4)}

# import .csv for all files to analyze
# save figure with whole trajectory
# snip trajectories and produce table
# extract mean speed, standard deviation of angle, mean speed through water, vessel heading
# plot bearing of boat VS angle of effective movement

BASE_FOLDER = "/home/mtomasini/Documents/06_Development/01_Maritime_Encounters/Field_data/Navigation_Data"

if len(sys.argv) > 1:
    name = sys.argv[1]
    dataset_address = sys.argv[2]
    start_time = sys.argv[3]
    latitude_clip = sys.argv[4]
    longitude_clip = sys.argv[5]
else:
    raise NameError(f"Wrong number of arguments!")


# print(BASE_FOLDER + dataset_address)

full_data_raw = pd.read_csv(BASE_FOLDER + dataset_address, parse_dates = ['Time'], on_bad_lines='skip', encoding='windows-1252')
full_data = cut_transect(full_data_raw, start_time=start_time)

position = full_data[full_data["Name"] == "Position, Rapid Update"].dropna(axis=1)
position = position[-position["Latitude"].str.contains(latitude_clip)]
position = position[position["Longitude"].str.contains(longitude_clip)]

# create trajectory with map
plot_trajectory(position, with_speed=False, save_figure=True, plot_title="./Figures/Analyses/01_trajectory.png")

position['Converted Lat'] = position['Latitude'].apply(lambda x: coordinate_conversion(x))
position['Converted Lon'] = position['Longitude'].apply(lambda x: coordinate_conversion(x))
position_stripped = position[['Time', 'Converted Lat', 'Converted Lon']]
trajectory = mpd.Trajectory(position_stripped, traj_id = name, t='Time', x='Converted Lon', y='Converted Lat', crs="EPSG:4326")

# create trajectory with speed but without map
trajectory.plot(column='speed', vmax=2.0, **plot_defaults).get_figure().savefig('./Figures/Analyses/02_just_trajectory.png')

# split trajectories and create dataframe
# split = mpd.SpeedSplitter(trajectory).split(speed=1, duration=timedelta(seconds=10), min_length=500)
split = mpd.StopSplitter(trajectory).split(min_duration=timedelta(seconds=60), 
                                           max_diameter=50, 
                                           min_length=300)
trajectory_df = split.to_traj_gdf()

fig, axes = plt.subplots(nrows=1, ncols=len(split), figsize=(10,5))
for i, traj in enumerate(split):
    traj.plot(ax=axes[i], linewidth=5.0, capstyle='round', column='speed', vmax=20)
    
fig.savefig('./Figures/Analyses/03_split_trajectories.png')

trajectory_df["duration"] = trajectory_df.apply(lambda row: (row["end_t"] - row["start_t"]).total_seconds(), axis=1)
trajectory_df["speed"] = trajectory_df.apply(lambda row: row["length"] / row["duration"], axis=1)

trajectory_df["speed_water"] = None
trajectory_df["bearing"] = None
trajectory_df["wind_direction"] = None
trajectory_df["wind_speed"] = None
trajectory_df["check_manually"] = None
 
speed_water_ref = full_data[full_data["Name"] == "Speed, Water Referenced"].dropna(axis=1)
wind_data = full_data[full_data["Name"] == "Wind Data"].dropna(axis=1)

for i, traj in enumerate(split):

    try:
        if len(speed_water_ref) > 0:
            speed_through_water = calculate_mean_speed_through_water(traj, speed_water_ref)
            if 0.9*trajectory_df["speed"].iloc[i] <= speed_through_water <=  1.1*trajectory_df["speed"].iloc[i]:
                trajectory_df["check_manually"].iloc[i] = False
            else:
                trajectory_df["check_manually"].iloc[i] = True
        else:
            speed_through_water = None
            trajectory_df["check_manually"].iloc[i] = None
    except:
        speed_through_water = None
        trajectory_df["check_manually"].iloc[i] = "Error occurred"
    
    trajectory_df["speed_water"].loc[i] = speed_through_water
    
    # calculate mean bearing in transect 
    heading = full_data[full_data["Name"] == "Vessel Heading"].dropna(axis=1)
    trajectory_df["bearing"].iloc[i] = calculate_bearing(traj, heading)
    
    try:
        if len(wind_data) > 0:
            trajectory_df["wind_direction"].iloc[i], trajectory_df["wind_speed"].iloc[i] = calculate_winds(traj, wind_data)
        else:
            trajectory_df["wind_direction"].iloc[i] = None
            trajectory_df["wind_speed"].iloc[i] = None
    except:
        trajectory_df["wind_direction"].iloc[i] = None
        trajectory_df["wind_speed"].iloc[i] = None
        trajectory_df["check_manually"] = "Error occurred"

trajectory_df.to_csv("./Figures/Analyses/trajectories.csv")