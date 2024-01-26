import pandas as pd
from processing import coordinate_conversion
import movingpandas
from datetime import timedelta
from holoviews import opts
import hvplot.pandas
import matplotlib.pyplot as plt
import cartopy
import geopandas


def cut_transect(dataset, start_time, end_time=None):
    """Function generating a separate dataset for a given transect. 

    Args:
        dataset (pd.DataFrame): The dataset being cut to a transect.
        start_time (str): String containing a start time for the transect. Format is %H:%M:%s.
        end_time (str): String containing a start time for the transect. Format is %H:%M:%s.

    Returns:
        pd.DataFrame: Dataset cut between indicated start and end. 
    """
    # select first row corresponding to start time
    # 
    start_time = pd.Timestamp(start_time)#.time()
    
    if not end_time:
        start_row = dataset[dataset["Time"] > start_time].index[0]# dataset[dataset["Time"].str.contains(start_time)].index[0]
        new_dataset = dataset.loc[start_row:]
    else:
        end_time = pd.Timestamp(end_time)#.time()
        start_row = dataset[dataset["Time"] > start_time].index[0] # dataset[dataset["Time"].str.contains(start_time)].index[0]
        end_row = dataset[dataset["Time"] <= end_time].index[-1] # dataset[dataset["Time"].str.contains(end_time)].index[-1]
        new_dataset = dataset.loc[start_row:end_row]
    
    return new_dataset


def plot_trajectory(position_dataset, with_speed=False, seconds_binning=5, save_figure=False, plot_title="trajectory.png"):
    """Plot to generate interactive trajectory with colors for speed (if with_speed = True).

    Args:
        position_dataset (pd.DataFrame): dataset with GPS positions and time. 
        with_speed (bool, optional): If True, uses color map to indicate speed on trajectory. Defaults to False.
        seconds_binning (int, optional): How coarse is the trajectory. Defaults to 5.
    """
    position_dataset['Converted Lat'] = position_dataset['Latitude'].apply(lambda x: coordinate_conversion(x))
    position_dataset['Converted Lon'] = position_dataset['Longitude'].apply(lambda x: coordinate_conversion(x))
    # position_dataset['Converted Time'] = position_dataset['Time'].apply(lambda x: pd.to_datetime(x))
    
    position_stripped = position_dataset[['Time', 'Converted Lat', 'Converted Lon']]
    trajectories = movingpandas.Trajectory(position_stripped, traj_id = 'logboat', t='Time', x='Converted Lon', y='Converted Lat', crs="EPSG:4326")
    trajectories = movingpandas.MinTimeDeltaGeneralizer(trajectories).generalize(tolerance=timedelta(seconds=seconds_binning))
    
    opts.defaults(opts.Overlay(active_tools=['wheel_zoom'], frame_width=500, frame_height=500))
    hvplot_defaults = {'cmap':'Viridis', 'colorbar':True, 'figsize':(5,4)}
    
    if with_speed:
        plot = trajectories.to_crs({'init': 'epsg:4326'}).hvplot(title="Trajectories with current speed (m/s)", geo=True, c='speed')    
    else:
        plot = trajectories.to_crs({'init': 'epsg:4326'}).hvplot(title="Trajectories", geo=True)
        
    if save_figure:
        hvplot.save(plot, plot_title)
    else:
        hvplot.show(plot)
    
    
def plot_direction(dataset, start_time, end_time, number_of_ticks = 5):
    transect = cut_transect(dataset, start_time, end_time)

    indexes_ticks = [0]
    transect_size = len(transect)
    for i in range(1, number_of_ticks + 1):
        tick = i * transect_size // number_of_ticks - 1 
        indexes_ticks.append(tick)
        
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(transect["Heading Sensor Reading"], range(0, transect.shape[0]), '.')
    ax.set_rticks(indexes_ticks)
    ax.set_yticklabels(transect["Time"].iloc[indexes_ticks].values)
    ax.set_theta_zero_location('N')
    
    return fig


def plot_static_trajectory():
    fig, ax = plt.subplots(subplot_kw={'projection': cartopy.crs.PlateCarree()}, figsize=(20,10))

    # Choose coastline resolution
    ax.coastlines('50m')

    # Limit map to bounding box
    ax.set_extent([bbox[0], bbox[2], bbox[1], bbox[3]], cartopy.crs.PlateCarree())

    # Add ocean and land features, for visuals
    ax.add_feature(cartopy.feature.OCEAN, zorder=0)
    ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')

    # Adds gridds to visual
    ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.2, linestyle='--')

    date = dates_seasons[season]
    
    ax.set_title(f"{season.capitalize()} {north_or_south} trajectories (date: {date})")
    
    
def plot_towing(dataset, boat, orientation, number_of_people, save = False):
    selection = dataset[dataset["boat"] == boat]
    selection = selection[selection["no_people"] == number_of_people]
    selection = selection[selection["orientation"] == orientation]
    weight = selection["weight"].iloc[0]
    
    plt.errorbar(selection.speed, selection.force, yerr=50, fmt='-o')
    plt.xlabel("Speed [kn]", fontsize = 14)
    plt.ylabel("Force [N]", fontsize = 14)
    plt.title(f"{orientation} towing, boat: {boat}, weight: {weight} kg ({number_of_people} people)", fontsize=15)
    plt.xticks(fontsize = 14)
    plt.yticks(fontsize = 14)
    plt.xlim(0, 7)
    plt.ylim(0, 700)
    plt.grid()
    
    if save:
        boat_name = boat.replace(".5", "")
        plt.savefig(f"./Figures/Towing/towing_{orientation.lower()}_{boat_name}_{number_of_people}people.png")
    
def plot_towing_by_weight(dataset, boat, orientation, save = False):
    selection = dataset[dataset["boat"] == boat]
    selection = selection[selection["orientation"] == orientation]
    
    fig, ax = plt.subplots()
    
    for weight in selection.weight.unique():
        selection_to_plot = selection[selection["weight"] == weight]
        # ax.plot(selection_to_plot.speed, selection_to_plot.force, '-o')
        ax.errorbar(selection_to_plot.speed, selection_to_plot.force, yerr=50, fmt='-o')
    
    ax.set_xlabel("Speed [kn]", fontsize = 14)
    ax.set_ylabel("Force [N]", fontsize = 14)
    
    ax.set_title(f"{orientation} towing, boat: {boat}, by weight", fontsize=15)
    # ax.set_xticks(fontsize = 14)
    # ax.set_yticks(fontsize = 14)
    ax.tick_params(axis='both', which='major', labelsize=14)
        
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 700)
    ax.grid()
        
    ax.legend([f"{weight} kg" for weight in selection.weight.unique()], fontsize = 12)
    
    if save:
        boat_name = boat.replace(".5", "")
        fig.savefig(f"./Figures/Towing/ByWeight/towing_{orientation.lower()}_{boat_name}.png")
        

def plot_towing_by_orientation(dataset, boat, number_of_people, save = False):
    selection = dataset[dataset["boat"] == boat]
    selection = selection[selection["no_people"] == number_of_people]
    
    fig, ax = plt.subplots()
    
    for orientation in selection.orientation.unique():
        selection_to_plot = selection[selection["orientation"] == orientation]
        # ax.plot(selection_to_plot.speed, selection_to_plot.force, '-o')
        ax.errorbar(selection_to_plot.speed, selection_to_plot.force, yerr=50, fmt='-o')
    
    ax.set_xlabel("Speed [kn]", fontsize = 14)
    ax.set_ylabel("Force [N]", fontsize = 14)
    
    ax.set_title(f"Towing experiment, boat: {boat}, {number_of_people} people, by orientation", fontsize=15)
    # ax.set_xticks(fontsize = 14)
    # ax.set_yticks(fontsize = 14)
    ax.tick_params(axis='both', which='major', labelsize=14)
        
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 700)
    ax.grid()
        
    ax.legend([f"{orientation} " for orientation in selection.orientation.unique()], fontsize = 12)
    
    if save:
        boat_name = boat.replace(".5", "")
        fig.savefig(f"./Figures/Towing/ByOrientation/towing_{number_of_people}people_{boat_name}.png")
        
        
def calculate_mean_speed_through_water(traj, speed_water_dataset, max_speed = 5):
    start_time = traj.get_start_time().strftime("%H:%M:%S")
    end_time = traj.get_end_time().strftime("%H:%M:%S")
    
    speed_water_ref_transect = cut_transect(speed_water_dataset, start_time, end_time)
    
    speeds = speed_water_ref_transect["Speed Water Referenced"]
    
    # purge exaggerate speeds
    if len(speeds) > 0:
        speeds = speeds[speeds <= max_speed]
        average_speed = speeds.mean() # speed_water_ref_transect["Speed Water Referenced"].mean()
    else: 
        average_speed = None

    return average_speed


def calculate_bearing(traj, heading_dataset):
    start_time = traj.get_start_time().strftime("%H:%M:%S")
    end_time = traj.get_end_time().strftime("%H:%M:%S")
    
    vessel_heading = cut_transect(heading_dataset, start_time, end_time)
    
    headings = vessel_heading["Heading Sensor Reading"]
    
    average_heading = headings.mean() # speed_water_ref_transect["Speed Water Referenced"].mean()
    
    return average_heading


def calculate_winds(traj, winds_dataset):
    start_time = traj.get_start_time().strftime("%H:%M:%S")
    end_time = traj.get_end_time().strftime("%H:%M:%S")
    
    wind_transect = cut_transect(winds_dataset, start_time, end_time)
    
    wind_directions = wind_transect["Wind Direction"]
    wind_speeds = wind_transect["Wind Speed"]
    
    average_direction = wind_directions.mean() # speed_water_ref_transect["Speed Water Referenced"].mean()
    average_speed = wind_speeds.mean()
    
    return average_direction, average_speed