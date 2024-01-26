import re
import pandas as pd

def concatenate_datasets(list_of_datasets):
    # create first dataframe
    data = pd.read_csv(list_of_datasets[0], encoding='windows-1252')
    for dataset in list_of_datasets[1:]:
        next_dataset = pd.read_csv(dataset, encoding='windows-1252')
        data = pd.concat([data, next_dataset], ignore_index=True)
    
    return data    


def coordinate_conversion(coordinate: str) -> float:
    """Receives coordinates as a string, e.g. "48°36.05' N" and turns it into a float number, such as 48.

    Args:
        coordinate (str): _description_

    Returns:
        float: _description_
    """
    
    degrees, minutes, direction = re.split('[°\']', coordinate)
    direction = direction.replace(" ", "")
    converted_coordinate = (float(degrees) + float(minutes)/60) * (-1 if direction in ['W', 'S'] else 1)
    
    return converted_coordinate