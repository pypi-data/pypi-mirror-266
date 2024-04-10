from typing import Optional, List, Dict
import datetime
import pandas as pd
import numpy as np
import h5py

from .Snowpack import special_codes, Snowpack

OLD_HEADER = "hand hardness either (N) or index steps (1)"
WEAK_LAYER = "position (cm) and minimum stability indices"
SURFACE_HOAR = ["grain type" ,"grain size (mm)"  ,"and density (kg m-3) of SH at surface"]

class SnowpackReader:
    """A class for reading and parsing Snowpack files."""
    
    def __init__(self, filename: str):
        """
        Initializes a SnowpackReader object.
        
        The data and units are saved with the data codes as keys.
        
        So to get a data column for a parameter use data[date][code] to get the data at a specific date and units[code] to get the unit.
        
        Conversion from Codes to names and vice versa is available through the DataCodes and NamesToCodes dictionaries.

        Args:
            filename (str): The path to the Snowpack file.
            meaningful_names (bool, optional): If True, the data codes will be replaced with meaningful names given in the header, in the returned dataframe

        Attributes:
            filename (str): The path to the Snowpack file.
            metadata (dict, optional): A dictionary containing metadata information. Initialized as None.
            DataCodes (dict): A dictionary containing default data codes. Initialized with get_default_codes().
            data (dict): A dictionary to store the data read from the Snowpack file, each date is a key, and profiles are safed as Snowpack objects
            units (dict): A dictionary to store the units of the data.

        It is advised to use the Classes getter methods to get the data:
        Methods:
            get_profile_on(date: datetime.datetime) -> Snowpack: Returns the data for the given date.
            get_all_profiles() -> List[Snowpack]: Returns all the profiles.
            get_var(code:str) -> List[np.ndarray]: Returns the data for the given code.
            CodeToName(code:str) -> str: Returns the name of the code.
        
        If you do not want to have data below ground level, use the discard_below_ground method.
        Methods:
            discard_below_ground(discard: bool): Getter and writers only use the above ground data.
        
        To write to another file format use the toCSV and toHDF5 methods. It is advised to use the HDF5 format as it is much more robust
        Methods: 
            toCSV(filename:str, integrate:bool=False): Writes the data to a CSV file.
            toHDF5(filename:str, integrate:bool=False): Writes the data to a HDF5 file.
            
        Reader Methods to read the data from a file written by this class:
            readHDF5(filename:str) -> dict, dict: Reads the data from a HDF5 file.
            fromCSV(filename:str) -> dict, dict: Reads the data from a CSV file written by the toCSV method.

        """
        self.filename = filename
        
        # file content
        self.metadata = {}
        self.DataCodes = {}
        self.units = {}
        self.data:Dict[datetime.datetime,Snowpack] = {}
        
        # internal help variables
        self.current_date = None
        self._old_hardness = False
        
        self._read_file()
        self._clear_mapping()
        self._parse_profiles()
        

    def _read_file(self):
        """Reads and parses the Snowpack file"""
        try:
            with open(self.filename, 'r') as file:
                self._parse_file(file)
        except (FileNotFoundError, PermissionError) as e:
            raise(f"Error opening file: {e}")
            # Handle error appropriately

    def _parse_file(self, file):
        """
        Parses the Snowpack file line by line.

        Args:
            file (file object): The file object to parse.
        """
        current_section = None
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty or comment lines
                continue
            current_section, new_section  = self._determine_section(line, current_section)
            if new_section:
                continue
            self._parse_sections(line, current_section)

    def _determine_section(self, line: str, current_section: str) -> str:
        """
        Determines the current section based on the line content.

        Args:
            line (str): The line to analyze.
            current_section (str): The current section.

        Returns:
            str: The updated current section.
        """
        if "STATION_PARAMETERS" in line:
            return 'metadata', True
        elif "HEADER" in line:
            return 'header', True
        elif "DATA" in line:
            return 'data', True
        return current_section, False
    
    def _parse_header(self, line:str, current_section:str):
        """
        Parses the header sections [STATION_PARAMETERS] and [HEADER].

        Parameters:
        - line (str): The line to parse.
        - current_section (str): The current section.
        """
        if current_section == "metadata":
            key, value = line.split('=')
            self.metadata[key.strip()] = value.strip()            
        elif current_section == 'header':
            line_vals = line.split(',')
            if line_vals[0] == '0500' and line_vals[1] == 'Date':
                self.DataCodes["0500"] = "Date"
            elif line_vals[0] == '0530':
                self.DataCodes["0530"] = "minimum stability indices (cm)"
            elif line_vals[0] == '0514':
                self.DataCodes["0514"] = "surface hoar ([Swiss Code, mm, kgm-3])"
            elif line_vals[0] == '0534':
                self._old_hardness = line_vals[2] == OLD_HEADER
            else:
                if len(line_vals) >= 3:
                    self.DataCodes[line_vals[0]] = ",".join(line_vals[2:])
                else:
                    self.DataCodes[line_vals[0]] = line_vals[2]

    def _parse_data_section(self, line:str):
        """Parses the [DATA] section"""
        
        vals = [val.strip() for val in line.split(',')]
        code = vals[0]
        if len(code)!=4: raise ValueError("Invalid data code: {}".format(code));
        if vals[1] == "nElems" or vals[1] == "grain":
            print("Incorrect header section, continuing anyways.")
            self._parse_header(line, "header")
        

        # parse the data lines    
        if code == '0500':
            self.current_date = datetime.datetime.strptime(vals[1], '%d.%m.%Y %H:%M:%S')
            self.data[self.current_date] = Snowpack()
            return None
        
        n_elements = int(vals[1])
        elements = vals[2:]
       
        elements_arr = np.array(elements).astype(float)        
        self.data[self.current_date].set_param(code, elements_arr, n_elements)
        
    def _parse_sections(self, line:str, current_section:str):
        if current_section == "metadata" or current_section == "header":
            self._parse_header(line, current_section)
        elif current_section == "data":
            self._parse_data_section(line)
        else:
            raise ValueError("Invalid section: {}".format(current_section))
        
        
    def _clear_mapping(self):
        """Clears the mapping of data codes"""
        for k, v in self.DataCodes.items():
            if "(" in v and ")" in v:
                unit = v.split("(")[1].split(")")[0]
            else:
                unit = "b.E."
            self.units[k] = unit  
            self.DataCodes[k] = v.split("(")[0].strip()
        self.DataCodes = {k : v.split("[")[0].strip() for k, v in self.DataCodes.items()}
        self.NamesToCodes = {v: k for k, v in self.DataCodes.items()}
        
    def _parse_profiles(self):
        """Parses the profiles"""
        for date in self.data:
            self.data[date]._parse_data(self._old_hardness)

    def update_name_of_code(self, code: str, name: str):
        """Updates the name of the code"""
        if code not in self.DataCodes:
            raise ValueError(f"{code} not found. Available codes are: {', '.join(self.DataCodes.keys())}")
        self.DataCodes[code] = name
        self.NamesToCodes[name] = code
    
    def name_to_code(self, name: str) -> str:
        """Returns the code for the given name"""
        try:
            return self.NamesToCodes[name]
        except KeyError:
            print(f"{name} not found. Available names are: {', '.join(self.NamesToCodes.keys())}")
            raise
                
    def discard_below_ground(self, discard: bool = True):
        """Will only return the above ground data.

        Args:
            discard (bool): If True, below ground data will be discarded. If False, below ground data will be included.

        """
        for date in self.data:
            self.data[date].discard_below_ground(discard)
    
    def get_profile_nr(self, nr: int) -> Snowpack:
        """Returns the profile for the given number"""
        return self.data[self.get_all_dates()[nr]]
                
    def get_profile_on(self, date: datetime.datetime) -> Snowpack:
        """
        Returns the data for the given date.

        Args:
            date (datetime.datetime): The date for which to retrieve the data.

        Returns:
            pandas.DataFrame: The snowpack profile for the given date.
        """
        if date in self.get_all_dates():
            return self.data[date]
        else:
            return None

    def get_all_dates(self) -> List[datetime.datetime]:
            """Returns all the dates in the data.

            Returns:
                list: A list of all the dates in the data.
            """
            return list(self.data.keys())
    
    def get_all_profiles(self)-> List[Snowpack]:
        """
        Returns all the profiles.

        Returns:
            list: returns a list of profiles for each date.
        """
        return [self.get_profile_on(date) for date in self.get_all_dates()]
    
    
    def get_var(self, code:str):
        """Returns the data for the given code"""
        return [self.get_snowpack_on(date).get_param(code) for date in self.get_all_dates()]
    
    
    def toCSV(self, filename:str, integrate:bool=False):
            """Writes the data to a CSV file
            
            Args:
                filename (str): The name of the CSV file to write the data to.
                integrate (bool, optional): Whether to integrate the special information into the dataframe or keep it as additional information.

            Special information is 0514: surface hoar and 0530: minimum stabiliy index
            """
            # first write the metadata
            with open(filename, 'w') as file:
                file.write("# This file was created with the SnowpackReader library, which also provides a method to read this file.\n")
                file.write("# [METADATA]\n")
                for key, value in self.metadata.items():
                    file.write("# {} = {}\n".format(key, value))
                
                file.write("# [DATA]\n")
                for date in self.get_all_dates():
                    file.write("# Date = {}\n".format(date.strftime('%d.%m.%Y %H:%M:%S')))
                    profile = self.get_profile_on(date)
                    if profile.weak_layer is not None:
                        file.write(f"# 0530, weak layer, {', '.join(map(str, profile.weak_layer))}\n")         
                    if profile.surface_hoar is not None:
                        file.write(f"# 0514, surface hoar, {', '.join(map(str, profile.weak_layer))}\n")         
                    profile.toDf(integrate=integrate).to_csv(file, index=False, mode='a')
    
    def toHDF5(self, filename:str, integrate:bool = False):
            """Writes the data to a HDF5 file
            
            Args:
                filename (str): The name of the HDF5 file to write the data to.
                integrate (bool, optional): Whether to integrate the special information into the dataframe or keep it as additional information.
            
            Special information is 0514: surface hoar and 0530: minimum stabiliy index
            """
            with h5py.File(filename, 'w') as file:
                for key, value in self.metadata.items():
                    file.attrs[key] = value
                
                for date in self.get_all_dates():
                    group = file.create_group(date.strftime('%d.%m.%Y %H:%M:%S'))
                    profile = self.get_profile_on(date)
                    if profile.weak_layer is not None:
                        group.attrs['weak_layer'] = profile.weak_layer
                    if profile.surface_hoar is not None:
                        group.attrs['surface'] = profile.surface_hoar
                    df = profile.toDf(integrate=integrate)
                    col_names = list(df.columns)
                    arr = df.to_numpy()
                    group.attrs["fields"] = col_names
                    group.create_dataset("data", data=arr)

    def __str__(self):
        ss = "PRO File:\n"
        ss += "Filename: {}\n".format(self.filename)
        ss += "Metadata: {}\n".format(self.metadata)
        ss += "Data codes: {}\n".format(self.DataCodes)
        ss += "Units: {}\n".format(self.units)
        ss += "Dates: {}\n".format(self.get_all_dates())
        return ss
    
    def info(self):
        print(self)
        
        
            
                
        
def readPRO(filename:str):
    """
    Reads the snowpack file and returns a SnowpackReader object.

    Args:
        filename (str): The path to the snowpack file.

    Returns:
        SnowpackReader: The SnowpackReader object representing the snowpack file.
    """
    return SnowpackReader(filename)


def readHDF5(filename:str):
    """Reads the data from a HDF5 file

    Args:
        filename (str): The name of the HDF5 file to read the data from.

    Returns:
        dict: The metadata.
        dict: A dictionary where each date contains a dataframe with the profile.
    """
    metadata = {}
    data = {}

    with h5py.File(filename, 'r') as file:
        # Read metadata
        for key, value in file.attrs.items():
            metadata[key] = value
        
        # Read data
        for date in file.keys():
            group = file[date]
            weak_layer = group.attrs.get('weak_layer', None)
            surface_hoar = group.attrs.get("surface_hoar", None)
            col_names = group.attrs.get("fields")
            dat = group.get("data")
            data[date] = pd.DataFrame(dat[:], columns=col_names)
            

    return metadata, data


def readCSV(filename:str):
    """Reads the data from a CSV file written by the toCSV method
    
    Args:
        filename (str): The name of the CSV file to read the data from.
        
    Returns:
        dict: The metadata.
        dict: A dictionary where each date contains a dataframe with keys: data, weak_layer, surface_hoar.
                data is the dataframe for the respective date, and weak_layer and surface_hoar contain (if available) numpy arrays with the respective information
    """
    metadata = {}
    dataframes = {}
    df_start_lines = [0]
    df_end_lines = []
    counter = 0
    with open(filename, 'r') as file:
        lines = file.readlines()
        date = None
        section = ""
        for line_id, line in enumerate(lines):
            if "METADATA" in line:
                section = "metadata"
                continue
            elif "DATA" in line:
                section = "data"
                continue
            if line.startswith('#') and section == "metadata":
                key, value = line[2:].strip().split(' = ')
                metadata[key] = value
            elif line.startswith('#') and section == "data":
                if "Date" in line:
                    date = datetime.datetime.strptime(line.split('=')[1].strip(), '%d.%m.%Y %H:%M:%S')
                    dataframes[date] = {"data": []}
                    counter = line_id
                    df_end_lines.append(line_id)
                elif "weak layer" in line:
                    dataframes[date]["weak_layer"] = np.array(line.split(',')[2:], dtype=float)
                    counter = line_id
                elif "surface hoar" in line:
                    dataframes[date]["surface_hoar"] = np.array(line.split(',')[2:],dtype=float)
                    counter = line_id
            else:
                if counter not in df_start_lines:
                    df_start_lines.append(counter)
        df_start_lines.pop(0)
        df_end_lines.pop(0)
        
    for id, date in enumerate(dataframes.keys()):
        dataframes[date]["data"] = pd.read_csv(filename,  skiprows=df_start_lines[id], nrows=df_end_lines[id]-df_start_lines[id]-1)
    
    return metadata, dataframes