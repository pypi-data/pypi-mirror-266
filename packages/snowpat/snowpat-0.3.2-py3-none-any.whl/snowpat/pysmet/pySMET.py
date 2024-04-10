from .SMET import SMETFile
from .MetaData import Location

from typing import List
import os

def read(filename: str) -> SMETFile: 
    """Reads a file in SMET format and returns a SMETFile object representing the file.

    This function reads a file in SMET format and creates a SMET object that provides access to the data and metadata in the file. The data can be accessed via the `data` attribute of the returned object. The metadata is divided into three categories: standard metadata, optional metadata, and ACDD metadata, which can be accessed via the `meta_data.key`, `optional_meta_data.key`, and `acdd_meta_data.key` attributes, respectively.

    Args:
        filename (str): The path to the SMET file.

    Returns:
        SMETFile: A SMET object representing the file. The following attributes are available:
            - `data`: The data from the SMET file, as a pandas DataFrame.
            - `meta_data.key`: The standard metadata from the SMET file.
            - `optional_meta_data.key`: The optional metadata from the SMET file.
            - `acdd_meta_data.key`: The ACDD (Attribute Convention for Data Discovery) metadata from the SMET file.

    Examples:
        >>> import pysmet as smet
        >>> file = smet.read("path/to/smet/file")
        >>> data = smet.data
        >>> data_numpy = smet.toNumpy()
        >>> location_lat = smet.meta_data.location.lat
        >>> location_lon = smet.meta_data.location.lon
        >>> acdd_creator_name = smet.acdd_meta_data.get_attribute("creator_name")
        >>> smet.info() # Print a summary of the SMET file
    """
    num_header_lines = 0
    with open(filename, 'r') as f:
        for line in f:
            num_header_lines += 1
            if "[DATA]" in line:
                break
    
    return SMETFile(filename, read=True, num_header_lines=num_header_lines)

def locFromEPSG(epsg: int, x: float, y: float, z:float=None) -> Location:
    """
    Create a Location object from EPSG code, x, y, and optional z coordinates.

    Args:
        epsg (int): The EPSG code of the location.
        x (float): The x-coordinate of the location.
        y (float): The y-coordinate of the location.
        z (float, optional): The z-coordinate of the location. Defaults to None.

    Returns:
        Location: The created Location object.
    """
    loc = Location()
    loc.epsg = epsg
    loc.easting = x
    loc.northing = y
    loc.altitude = z
    return loc

def locFromLatLon(lat: float, lon: float, alt: float=None) -> Location:
    """
    Create a Location object from latitude, longitude, and altitude.

    Args:
        lat (float): The latitude value.
        lon (float): The longitude value.
        alt (float, optional): The altitude value. Defaults to None.

    Returns:
        Location: The created Location object.
    """
    loc = Location()
    loc.latitude = lat
    loc.longitude = lon
    loc.altitude = alt
    return loc

def merge_files(files : List[str]):
    """
    Merge multiple SMET files into a single SMET file.

    Args:
        files (List[str]): A list of paths to the SMET files to merge.

    Returns:
        SMETFile: A SMET object representing the merged file. 
    """
    fsmet = read(files[0])
    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"File {file} not found")
        other_fsmet = read(file)
        fsmet.merge(other_fsmet)
    return fsmet