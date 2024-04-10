import pandas as pd
import numpy as np
import os

from .MetaData import *
from .ACDD import ACDDMetadata

from ..msgs import *

class SMETFile:
    """A class used to represent a SMET file.

    Attributes:
        identifier (str): A string that represents the identifier of the SMET data.
        meta_data (MetaData): An instance of the MetaData class that stores the mandatory metadata of the SMET data.
        data (pd.DataFrame): A pandas DataFrame that stores the SMET data.
        optional_meta_data (OptionalMetadata): A dictionary that stores the optional metadata of the SMET data.
        acdd_meta_data (ACDDMetadata): An instance of the ACDDMetadata class that stores the ACDD metadata of the SMET data.
        other_meta_data(dict): A dictionary that stores the other metadata of the SMET data.
    """

    def __init__(self, filename, read: bool, num_header_lines: int = None, fun:bool = False) -> None:
        if not os.path.isfile(filename) and read:
            raise FileNotFoundError(f"The file {filename} does not exist.")

        self.num_header_lines = num_header_lines if read else 1
        self.identifier = None if read else self.getIdentifier()
        self.optional_meta_data = None if read else dict()
        self.filename = filename
        self.data_header = None if read else ""
        self.acdd_meta_data = ACDDMetadata()
        self.other_meta_data = dict()
        self.meta_data = self.read_meta_data() if read else MetaData()
        self.data = self.read_data() if read else pd.DataFrame()

        self.fun = fun

    def read_data(self) -> pd.DataFrame:
        if not self.meta_data:
            print(
                "Something went wrong reading MetaData, in the worst case please contact patrick.leibersperger@slf.ch"
            )
        if self.meta_data.fields:
            self.data_header = self.meta_data.fields
        else:
            print("Unable to read data header from SMET file. Using no header.")

        data = pd.read_csv(
            self.filename, delimiter="\s+", skiprows=self.num_header_lines, header=None
        )
        if self.meta_data.nodata:
            data = data.replace(self.meta_data.nodata, np.nan)

        if self.data_header:
            data.columns = self.data_header
            data["timestamp"] = pd.to_datetime(data["timestamp"], format="ISO8601")
        return data

    def read_meta_data(self) -> MetaData:
        meta_data = MetaData()
        optional_meta_data = OptionalMetaData()
        with open(self.filename, "r") as f:
            self.identifier = next(f).strip()
            for line in f:
                if "[DATA]" in line:
                    break
                if "[HEADER]" in line:
                    continue
                val = line.split("=")[1].strip()
                if "station_id" in line:
                    meta_data.station_id = val
                elif "latitude" in line:
                    meta_data.location.latitude = float(val)
                elif "longitude" in line:
                    meta_data.location.longitude = float(val)
                elif "altitude" in line:
                    meta_data.location.altitude = float(val)
                elif "easting" in line:
                    meta_data.location.easting = float(val)
                elif "northing" in line:
                    meta_data.location.northing = float(val)
                elif "epsg" in line:
                    meta_data.location.epsg = int(val)
                elif "nodata" in line:
                    meta_data.nodata = float(val)
                elif "fields" in line:
                    meta_data.fields = self.__parseFields(val.split())
                elif "station_name" in line:
                    optional_meta_data.station_name = val
                elif "tz" == line.split("=")[0].strip():
                    optional_meta_data.tz = int(val)
                elif "slope_angle" in line:
                    optional_meta_data.slope_angle = float(val)
                elif "slope_azi" in line:
                    optional_meta_data.slope_azi = float(val)
                elif "creation" in line:
                    optional_meta_data.creation = val
                elif "source" in line:
                    optional_meta_data.source = val
                elif "units_offset" in line:
                    optional_meta_data.units_offset = list(map(float, val.split()))
                elif "units_multiplier" in line:
                    optional_meta_data.units_multiplier = list(map(float, val.split()))
                elif "comment" in line:
                    optional_meta_data.comment = val
                elif "acdd" in line:
                    key, value = line.split("=")
                    self.acdd_meta_data.set_attribute(key.strip(), value.strip())
                else:
                    self.other_meta_data[line.split("=")[0].strip()] = line.split("=")[1].strip()
        unknown_metadata = [key for key in self.other_meta_data.keys()]
        if unknown_metadata:
            if self.fun:
                print(bad())
                print(empire())
            print(f"Unknown metadata: {unknown_metadata}")
        meta_data.checkValidity(self.fun)
        self.optional_meta_data = optional_meta_data
        return meta_data

    def __parseFields(self, fields: List[str]):
        possible_fields = [
            "P",
            "TA",
            "TSS",
            "TSG",
            "RH",
            "VW",
            "DW",
            "ISWR",
            "RSWR",
            "ILWR",
            "OLWR",
            "PINT",
            "PSUM",
            "HS",
            "timestamp",
            "julian",
        ]
        non_conforming_fields = [
            field for field in fields if field not in possible_fields
        ]

        if non_conforming_fields:
            if self.fun:
                print(not_way())
                print(yoda())
            print(                    
                "The following fields do not conform to the SMET standard:",
                non_conforming_fields,
            )
        elif self.fun and not non_conforming_fields:
            print(way())
            print(mando())

        return fields

    def __str__(self):
        return (
            f"SMETFile:\n"
            f"{self.meta_data}\n"
            f"Optional MetaData: {self.optional_meta_data}\n"
            f"{self.acdd_meta_data}\n"
            f"Other MetaData: {self.other_meta_data}\n"
            f"Data:\n{self.data.head()}"
        )

    def toNumpy(self) -> np.ndarray:
        """Return a Numpy array of the data.

        This method uses the pandas DataFrame's to_numpy() method to convert the DataFrame to a Numpy array.

        Returns:
            np.ndarray: The data as a Numpy array.

        Examples:
            >>> instance = pysmet.read("path/to/file.smet")
            >>> array = instance.toNumpy()
        """

        return self.data.to_numpy()

    def toDf(self) -> pd.DataFrame:
        """Return the data as a pandas DataFrame.

        This method returns the data stored in the instance as a pandas DataFrame.

        Returns:
            pd.DataFrame: The data as a pandas DataFrame.

        Examples:
            >>> instance = pysmet.read("path/to/file.smet")
            >>> df = instance.toDf()
        """

        return self.data

    def info(self):
        """
        Print a summary of the SMET file.
        """
        print(self)

    def write(self, output_filename: str = None):
        """Writes the SMET file to disk.

        This method writes the SMET file , with the given metadata.
        If the 'timestamp' column exists in the data, it is formatted as an ISO 8601 string.

        Args:
            output_filename (str, optional): The path to the output file. If not provided, the original filename is used.

        Returns:
            None
        """
        output_filename = output_filename if output_filename else self.filename
        self.meta_data.checkValidity()
        out_data = self.data.copy()
        if self.meta_data.nodata:
            out_data = out_data.fillna(self.meta_data.nodata)

        if pd.api.types.is_datetime64_any_dtype(out_data["timestamp"].dtype):
            out_data["timestamp"] = out_data["timestamp"].apply(lambda x: x.isoformat())
        elif pd.api.types.is_string_dtype(out_data["timestamp"].dtype):
            try:
                out_data["timestamp"] = pd.to_datetime(out_data["timestamp"]).apply(
                    lambda x: x.isoformat()
                )
            except:
                pass
        else:
            print("The 'timestamp' column is neithr in string nor datetime format.")

        with open(output_filename, "w") as f:
            # Write identifier
            f.write(self.identifier + "\n")

            # Write [HEADER]
            f.write("[HEADER]\n")

            # Write metadata
            for key, value in self.meta_data.combined_dict.items():
                f.write(f"{key} = {value}\n")

            # Write optional metadata if it exists
            if self.optional_meta_data:
                for key, value in self.optional_meta_data.items():
                    f.write(f"{key} = {value}\n")

            # Write ACDD metadata if it exists
            if self.acdd_meta_data:
                for key, value in self.acdd_meta_data.adjusted_dict.items():
                    f.write(f"{key} = {value}\n")

            # Write [DATA]
            f.write("[DATA]\n")

            # Check if "timestamp" is in columns
            timestamp_exists = "timestamp" in self.data.columns

            # Write data
            for row in out_data.itertuples(index=False):
                if timestamp_exists:
                    f.write(
                        "\t".join(
                            (
                                f"{str(item):<20}"
                                if field == "timestamp"
                                else f"{str(item):<10}"
                            )
                            for field, item in zip(self.data.columns, row)
                        )
                        + "\n"
                    )
                else:
                    f.write("\t".join(f"{str(item):<20}" for item in row) + "\n")

    # for creating a smet file from scratch
    def getIdentifier(self, version=1.1) -> str:
        """Get the identifier for the SMET file.

        The identifier is the first line in a SMET file and is used to identify the file format.
        It is generated based on the provided version.

        Args:
            version (float, optional): The version number of the SMET file. Default is 1.1.

        Returns:
            str: The identifier for the SMET file.

        """

        self.num_header_lines += 1
        return f"SMET {version} ASCII"

    def setIdentifier(self, version=1.1) -> None:
        """Set the identifier for the SMET file.

        The identifier is the first line in a SMET file and is used to identify the file format.
        It is generated based on the provided version.

        Args:
            version (float, optional): The version number of the SMET file. Default is 1.1.

        Returns:
            None
        """

        self.num_header_lines += 1
        self.identifier = f"SMET {version} ASCII"

    def setData(self, data: pd.DataFrame):
        self.data = data
        fields = data.columns.to_list()
        if fields[0] == "0" or fields[0] == 0:
            print("Please provide a meaningful list of fields in the MetaData")
        else:
            print("Using fields: ", fields)
            self.meta_data.fields = fields

    def fromNumpy(
        self, data: np.ndarray, header: List[str], timestamp: Optional[List[str]] = None
    ) -> None:
        """
        Load data from a numpy array into the SMET object.

        Args:
            data (np.ndarray): The numpy array containing the data.
            header (List[str]): The list of column names for the data.
            timestamp (Optional[List[str]], optional): The list of timestamps for the data. Defaults to None.

        Returns:
            None
        """
        self.data = pd.DataFrame(data, columns=header)
        self.meta_data.fields = header
        self.num_header_lines += 1
        self.data_header = header
        if timestamp:
            self.data["timestamp"] = pd.to_datetime(timestamp)

    def setMetaData(self, key: str, value):
        """
        Sets the metadata attribute with the given key to the specified value.
        If the metadata attribute does not exist, it is added to the optional_meta_data dictionary.

        Args:
            key (str): The key of the metadata attribute.
            value: The value to set for the metadata attribute.

        Necessary Metadata:
            station_id: str
            location: Location
            nodata: float
            fields: List[str]

        Supported ACDD Keys:
            title
            summary
            keywords
            conventions
            id
            naming_authority
            source
            history
            comment
            date_created
            creator_name
            creator_url
            creator_email
            institution
            processing_level
            project
            geospatial_bounds
            geospatial_lat_min
            geospatial_lat_max
            geospatial_lon_min
            geospatial_lon_max
            geospatial_vertical_min
            geospatial_vertical_max
            time_coverage_start
            time_coverage_end
            Wigos ID

        Returns:
            None
        """
        if hasattr(self.meta_data, key):
            setattr(self.meta_data, key, value)
        elif "acdd" in key or (key in self.acdd_meta_data.attributes.keys()):
            print(f"Adding {key} to acdd_meta_data.")
            self.acdd_meta_data.set_attribute(key, value)
        else:
            print(
                f"MetaData does not have attribute {key}. Adding to optional_meta_data."
            )
            self.optional_meta_data[key] = value
        self.num_header_lines += 1
        
    def mergeFromFile(self, other_filename:str, override:bool = False):
        """
        Merge the data of the current SMET file with the data of another SMET file.

        Args:
            other_filename (str): The path to the other SMET file.
            override (bool, optional): If True, duplicates in the data of the current SMET file are overridden by the data of the other SMET file. If False, only missing values are filld. Defaults to False.

        Returns:
            None
        """
        n_header = 0
        with open(other_filename, 'r') as f:
            for line in f:
                n_header += 1
                if "[DATA]" in line:
                    break
        other = SMETFile(other_filename, read=True, num_header_lines=n_header)
        self.merge(self, other, override)

    def merge(self, other:'SMETFile', override=False):
        """
        Merge the data of the current SMET file with the data of another SMET file.
        
        Args:
            other (SMETFile): The other SMET file.
            override (bool, optional): If True, duplicates in the data of the current SMET file are overridden by the data of the other SMET file. If False, only missing values are filld. Defaults to False.
            
        Returns:
            None
        """
        if self.meta_data != other.meta_data:
            raise ValueError("The MetaData of the two SMET files are not equal.")
        self.optional_meta_data.join(other.optional_meta_data)
        self.acdd_meta_data.join(other.acdd_meta_data)
        
        # Set "timestamp" as index for both dataframes
        self.data.set_index("timestamp", inplace=True)
        other.data.set_index("timestamp", inplace=True)

        if override:
            self.data.update(other.data)
        else:
            self.data = self.data.combine_first(other.data)
            self.data = pd.concat([self.data, other.data])

        # timestamp is now a column again
        self.data.reset_index(inplace=True)
        # Sort by "timestamp"
        self.data.sort_values("timestamp", inplace=True)
        # Drop duplicates, keeping the last occurrence
        self.data.drop_duplicates(subset="timestamp", keep="first", inplace=True)
        # Reset the index again after dropping duplicates
        self.data.reset_index(drop=True, inplace=True)
        self.meta_data.checkValidity()
        print("Merged data from", other.filename)       