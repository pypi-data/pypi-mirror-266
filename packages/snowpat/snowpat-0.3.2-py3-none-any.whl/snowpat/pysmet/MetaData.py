from typing import Optional, List
import pandas as pd

from ..msgs import *
class MetaData:
    """A class used to represent the metadata of a SMET file.

    Attributes:
        station_id (str): The ID of the station.
        location (Location): The location of the station, which includes:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
            altitude (float): The altitude of the location.
            easting (float): The easting of the location.
            northing (float): The northing of the location.
            epsg (int): The EPSG code of the location.
        nodata (float): The value representing no data.
        fields (List[str]): The list of fields in the SMET file.
    """
    def __init__(self) -> None:
        self.station_id: str = ""
        self.location: Location = Location()
        self.nodata: Optional[float] = None
        self.fields: Optional[List[str]] = []
        
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, MetaData):
            return False
        isEqual = True
        if self.station_id != __value.station_id:
            isEqual = False
        elif self.location != __value.location:
            isEqual = False
        elif self.nodata != __value.nodata:
            isEqual = False
        elif self.fields != __value.fields:
            isEqual = False
        return isEqual

    def __str__(self):
        return (
            f"MetaData:\n"
            f"Station ID: {self.station_id}\n"
            f"{self.location}\n"
            f"No Data: {self.nodata}\n"
            f"Fields: {self.fields}"
        )

    @property
    def combined_dict(self):
        d = self.__dict__.copy()
        d.update(self.location.adjusted_dict)
        del d["location"]
        if d.get('fields') is not None:
                d['fields'] = ' '.join(d['fields'])
        return d    
    
        
    def checkValidity(self, fun:bool=False) -> bool:
        nodata_set = self.nodata is not None
        valid =  self.station_id and self.location.checkValidity() and nodata_set and self.fields
        if not valid:
            if fun:
                print(bad())
                print(empire())
            raise f"Invalid metadata: {self}"
        else :
            if fun:
                print(way())
                print(mando())
        return valid


class Location:
    def __init__(self) -> None:
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.altitude: Optional[float] = None
        self.easting: Optional[float] = None
        self.northing: Optional[float] = None
        self.epsg: Optional[int] = None
        
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Location):
            return False
        isEqual = True
        for k,v in self.adjusted_dict.items():
            if v != getattr(__value, k):
                isEqual = False
                break
        return isEqual

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    @property
    def adjusted_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def __str__(self):
        attributes = [
            ("Latitude", self.latitude),
            ("Longitude", self.longitude),
            ("Altitude", self.altitude),
            ("Easting", self.easting),
            ("Northing", self.northing),
            ("EPSG", self.epsg),
        ]
        attributes_str = ", ".join(
            f"{name}: {value}" for name, value in attributes if value is not None
        )
        return f"Location: ({attributes_str})"

    def checkValidity(self) -> bool:
        lat_long_alt_set = (
            self.latitude is not None
            and self.longitude is not None
            and self.altitude is not None
        )
        east_north_alt_set = (
            self.easting is not None
            and self.northing is not None
            and self.altitude is not None
        )

        return lat_long_alt_set or east_north_alt_set

class OptionalMetaData:
    """A class used to store optional metadata of a SMET file.

    Attributes:
        station_name (str): The name of the station.
        tz (int): The timezone of the station.
        slope_angle (float): The slope angle of the station.
        slope_azi (float): The slope azimuth of the station.
        creation (str): The creation date/time of the SMET file.
        source (str): The source of the SMET file.
        units_offset (List[float]): The list of unit offsets in the SMET file.
        units_multiplier (List[float]): The list of unit multipliers in the SMET file.
        comment (str): Any additional comments.
    """
    def __init__(self) -> None:
        self.station_name: Optional[str] = None
        self.tz: Optional[int] = None
        self.slope_angle: Optional[float] = None
        self.slope_azi: Optional[float] = None
        self.creation: Optional[str] = None
        self.source: Optional[str] = None
        self.units_offset: Optional[List[float]] = None
        self.units_multiplier: Optional[List[float]] = None
        self.comment: Optional[str] = None

    @property
    def adjusted_dict(self):
        d = self.__dict__.copy()
        if d.get('units_offset') is not None:
            d['units_offset'] = ' '.join(map(str, d['units_offset']))
        if d.get('units_multiplier') is not None:
            d['units_multiplier'] = ' '.join(map(str, d['units_multiplier']))
        return {k: v for k, v in d.items() if v is not None}


    def __str__(self):
        attributes = [
            ("Station Name", self.station_name),
            ("Timezone", self.tz),
            ("Slope Angle", self.slope_angle),
            ("Slope Azi", self.slope_azi),
            ("Creation", self.creation),
            ("Source", self.source),
            ("Units Offset", self.units_offset),
            ("Units Multiplier", self.units_multiplier),
            ("Comment", self.comment),
        ]
        attributes_str = "\n".join(
            f"{name}: {value}" for name, value in attributes if value is not None
        )
        return f"OptionalMetaData:\n{attributes_str}"
    
    def join(self, other: 'OptionalMetaData'):
        attributes = ['station_name', 'tz', 'slope_angle', 'slope_azi', 'creation', 'source', 
                      'units_offset', 'units_multiplier', 'comment']

        for attr in attributes:
            self_value = getattr(self, attr)
            other_value = getattr(other, attr)

            if not self_value and other_value:
                setattr(self, attr, other_value)
            elif self_value and other_value and self_value != other_value:
                print(f"Warning: {attr} mismatch: {self_value} != {other_value}")