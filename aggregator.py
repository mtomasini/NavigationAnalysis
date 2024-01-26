import pandas as pd
import datetime
import os

def convert_date(date_string):
    """Function transforming a date in format YYMMDD to a datetime date.

    Args:
        date_string (str): date in string format YYMMDD.
    Returns:
        date_converted (datetime): date in datetime format   
    """
    
    year, month, day = int(date_string[:2]) + 2000, int(date_string[2:4]), int(date_string[4:6])
    
    date_converted = datetime.datetime(year, month, day)
    
    return date_converted


FOLDER = "./Figures/Analyses/"

folders = os.listdir(FOLDER)

columns = ["Boat", "Start time", "Length [m]", 
           "Direction [deg]", "Duration [s]", "Speed [m/s]", 
           "Speed through Water [m/s]", "Avg Bearing [deg]", 
           "Avg Wind Direction [deg]", "Avg Wind Speed [m/s]"]
# aggregate_df = pd.DataFrame(None, columns=10)
# aggregate_df.columns = columns

aggregate_list = []

for folder in folders:
    trajectories = pd.read_csv(FOLDER + folder + "/trajectories.csv")
    
    folder_date = folder[:6]
    year, month, day = int(folder_date[:2]) + 2000, int(folder_date[2:4]), int(folder_date[4:6])
    # date = convert_date(folder_date)
    
    for index, trajectory in trajectories.iterrows():
        # new_trajectory_row = pd.Series(None, columns = columns)
        
        # extract name of boat and time of travel
        boat, old_date = trajectory["traj_id"].split("_")
        try:
            start_time = datetime.datetime.strptime(old_date, "%Y-%m-%d %H:%M:%S.%f")
        except:
            start_time = datetime.datetime.strptime(old_date, "%Y-%m-%d %H:%M:%S")
        
        start_time = start_time.replace(year = year, month = month, day = day)
        
        # new_trajectory_row["Boat"] = boat
        # new_trajectory_row["Start time"] = start_time
        # new_trajectory_row["Length [m]"] = trajectory["length"]
        # new_trajectory_row["Direction [deg]"] = trajectory["direction"]
        # new_trajectory_row["Duration [s]"] = trajectory["duration"]
        # new_trajectory_row["Speed [m/s]"] = trajectory["speed"]
        # new_trajectory_row["Speed through Water [m/s]"] = trajectory["speed_water"]
        # new_trajectory_row["Avg Bearing [deg]"] = trajectory["bearing"]
        # new_trajectory_row["Avg Wind Direction [deg]"] = trajectory["wind_direction"]
        # new_trajectory_row["Avg Wind Speed [m/s]"] = trajectory["wind_speed"]
        
        aggregate_list.append([boat, start_time, trajectory["length"], trajectory["direction"], trajectory["duration"], trajectory["speed"], 
                               trajectory["speed_water"], trajectory["bearing"], trajectory["wind_direction"], trajectory["wind_speed"]])
        
aggregate_df = pd.DataFrame(aggregate_list, columns = columns)
aggregate_df = aggregate_df.sort_values('Start time')
aggregate_df = aggregate_df.reset_index(drop=True)
aggregate_df.to_csv("./aggregate_trajectories.csv")