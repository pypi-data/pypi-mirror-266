import pandas as pd
import numpy as np
import warnings
from typing import Dict, Optional

special_codes = ["0514", "0530"]
plus_minus = "\u00B1"


class Snowpack:
    def __init__(self):
        """
        Initializes a Snowpack object. Used to handle snow profile data from Snowpack.

        Except for obtaining the original height in the .pro file it is advised to only use the getter methods to access the data.

        Attributes:
            layer_boundaries (np.ndarray): The height of the layer boundaries. (Height as written in the Snowpack output)

        Methods:
            get_param(code:str): Returns a parameter from the Snowpack object for the given data code.
            discard_below_ground(discard:bool): Sets whether to return data below ground level (default: True).
            toDf(integrate:bool): Converts the Snowpack object to a pandas DataFrame. With either integrated weak layer and surface hoar or as metadata accssible as: df.weak_layer; df.surface_hoar

        Args:
            None

        Returns:
            None
        """
        self.layer_boundaries: Optional[np.ndarray] = None
        self.data: Dict[str, np.ndarray] = {}
        self.surface_hoar: Optional[np.ndarray] = None
        self.weak_layer: Optional[np.ndarray] = None
        self.isNewton: Optional[bool] = None
        self.old_hardness: Optional[bool] = None

        # internal variables
        self._height_mask: Optional[np.ndarray] = None
        self._above_ground = False
        self.num_nodes = None
        self._parsed = False

    def set_param(self, code: str, values: np.ndarray, boundaries: int):
        if not self.num_nodes:
            self.num_nodes = boundaries
        if code == "0501":
            self.layer_boundaries = values
            self._height_mask = self.layer_boundaries >= 0
        elif code == "0514":
            self.surface_hoar = values
        elif code == "0530":
            self.weak_layer = values
        else:
            self.data[code] = values
        
    def get_param(self, code: str):
        """
        Retrieves the parameter associated with the given code.

        Args:
            code (str): The code of the parameter to retrieve.

        Returns:
            The parameter associated with the given code.

        Raises:
            KeyError: If the code is not found in the data.

        """
        # need to add these, because they were handled seperately and can also be called through different means
        possible_codes = list(self.data.keys()) + ["0501", "0530", "0514"]
        if not code in possible_codes:
            print(f"{code} is invalid")
            print("available codes are:")
            print(f"{self.data.keys()}")
            
        if code == "0501":
            if self._above_ground:
                mask = np.append(self._height_mask,True)
                return self.layer_boundaries[mask]
            else:
                return self.layer_boundaries

        if code == "0514":
            return self.surface_hoar
        if code == "0530":
            return self.weak_layer

        param = self.data[code]
        if self._above_ground:
            param = param[self._height_mask]
        return param

    def discard_below_ground(self, discard: bool):
        """
        Sets whether to return data below ground level.

        If set to true, only data above ground will be returned, by the getter methods.
        Otherwise all the data will be returned.

        Can be used subsequently.

        Args:
            discard (bool): If True, data below ground level will be discarded. If False, all data will be kept.

        Returns:
            None
        """
        self._above_ground = discard

    def _parse_data(self, old_hardness:bool):
        # snowpack sometimes does not explicitly put a boundary at 0, so we need to append that
        if self.layer_boundaries[0] > 0:
            self.num_nodes += 1
            self.layer_boundaries = np.insert(self.layer_boundaries, 0, 0)
            self._height_mask = np.insert(self._height_mask, 0, True)
        
        # nodes give the boundaries, but values are valid for the whole layer
        n_layers = self.num_nodes -1
        for key, val in self.data.items():
            # grain types has surface hoar as 0, and is specified with a dfferent code
            if key == "0513": 
                self.data[key] = np.delete(val, -1)
            # fill missing layers with nans
            if self.data[key].size != n_layers:
                self.data[key] = np.insert(
                    self.data[key], 0, [np.nan for _ in range(n_layers - self.data[key].size)]
                )


        # make new fields, so it is clearer, where the layers actually are
        layer_middle = [
            (self.layer_boundaries[i + 1] + self.layer_boundaries[i]) / 2
            for i in range(self.layer_boundaries.size - 1)
        ]
        layer_thicknes = [
            (self.layer_boundaries[i + 1] - self.layer_boundaries[i]) / 2
            for i in range(self.layer_boundaries.size - 1)
        ]

        layer_middle = np.array(layer_middle)
        layer_thicknes = np.array(layer_thicknes)

        self.data["layer middle"] = layer_middle
        self.data["layer thickness"] = layer_thicknes
        if len(self._height_mask) > n_layers:
            self._height_mask = np.delete(self._height_mask, -1)
        
        
        # check how the hardness is specified
        if old_hardness:
            self.isNewton = all(self.data["0534"] > 0)
            self.old_hardness = True
        else:
            self.isNewton = any(self.data["0534"] > 6) 
            self.old_hardness = False

    def toDf(self, CodesToName: Dict = None, integrate: bool = False):
        """
        Converts the Snowpack object to a pandas DataFrame.

        In the data frame the heights given in the Snowpack output, which essentially are the layer boundaries,
        are converted to the middle of the layers and the thickness of the layers, for a clean data frame.
        The original layer boundaries can easily be computed from that.

        The minimum stability indices (weak_layer) and surface hoar information are available as:
        df.weak_layer and df.surface_hoar. However, this information will not be passed on when merging... the dataframe
        as pandas does not handle this yet.

        Args:
            CodesToName (Dict, optional): A dictionary mapping column data codes to column names.

        Returns:
            DataFrame: The Snowpack data as a pandas DataFrame.
        """
        df = pd.DataFrame(self.data)
        cols = (
            ["layer middle"]
            + ["layer thickness"]
            + [
                col
                for col in df.columns
                if col != "layer middle" and col != "layer thickness"
            ]
        )
        df = df[cols]
        if self._above_ground:
            df = df[self._height_mask]

        if CodesToName:
            df.rename(columns=CodesToName, inplace=True)
        if integrate:
            df.weak_layer = None
            df.surface_hoar = None
            if self.surface_hoar is not None:
                df["surface hoar"] = [
                    np.nan for _ in range(df["layer middle"].size - 1)
                ] + [self.surface_hoar]
            if self.weak_layer is not None:
                df["weak layer"] = [self.weak_layer] + [
                    np.nan for _ in range(df["layer middle"].size - 1)
                ]
        else:
            warnings.filterwarnings('ignore', 'Pandas doesn\'t allow columns to be created via a new attribute name')
            df.weak_layer = self.weak_layer
            df.surface_hoar = self.surface_hoar
        return df
