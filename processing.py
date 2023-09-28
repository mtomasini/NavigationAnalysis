import re




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