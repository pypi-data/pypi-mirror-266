class ACDDMetadata:
    """A class used to represent the ACDD (Attribute Convention for Data Discovery) metadata.

    Attributes:
        attributes (dict): A dictionary that stores the standard ACDD metadata attributes.
        unknown_attributes (dict): A dictionary that stores any unknown ACDD metadata attributes.

    Methods:
        set_attribute(attribute_name: str, value: Any) -> None:
            Sets the value of the specified attribute. If the attribute is not a standard ACDD attribute, it is added to the unknown_attributes dictionary.
        get_attribute(attribute_name: str) -> Any:
            Returns the value of the specified attribute.
    """

    def __init__(self):
        self.attributes = {
            'title': None,
            'summary': None,
            'keywords': None,
            'conventions': None,
            'id': None,
            'naming_authority': None,
            'source': None,
            'history': None,
            'comment': None,
            'date_created': None,
            'creator_name': None,
            'creator_url': None,
            'creator_email': None,
            'institution': None,
            'processing_level': None,
            'project': None,
            'geospatial_bounds': None,
            'geospatial_lat_min': None,
            'geospatial_lat_max': None,
            'geospatial_lon_min': None,
            'geospatial_lon_max': None,
            'geospatial_vertical_min': None,
            'geospatial_vertical_max': None,
            'time_coverage_start': None,
            'time_coverage_end': None,
            'Wigos ID': None,
        }
        
        self.unknown_attributes = {}

    def set_attribute(self, attribute_name, value):
        # Remove 'acdd_' prefix if present
        attribute_name = attribute_name.replace('acdd_', '')

        if attribute_name in self.attributes:
            self.attributes[attribute_name] = value
        else:
            self.unknown_attributes[attribute_name] = value

    @property
    def adjusted_dict(self):
        d = {
            **{k: v for k, v in self.attributes.items() if v is not None},
            **{k: v for k, v in self.unknown_attributes.items() if v is not None}
        }
        return d
            
    def __str__(self):
        str_repr = "ACDD Attributes:\n"
        for attribute, value in self.attributes.items():
            if value is not None:
                str_repr += f"{attribute}: {value}\n"
        str_repr += "Unknown Attributes:\n"
        for attribute, value in self.unknown_attributes.items():
            if value is not None:
                str_repr += f"{attribute}: {value}\n"
        return str_repr
    
    def get_attribute(self, attribute_name):
        if attribute_name in self.attributes:
            return self.attributes[attribute_name]
        elif attribute_name in self.unknown_attributes:
            return self.unknown_attributes[attribute_name]
        else:
            print("Attribute not found")
    
    def join(self, other: 'ACDDMetadata'):
        for attr_dict in [other.attributes, other.unknown_attributes]:
            for attribute, value in attr_dict.items():
                self_value = self.get_attribute(attribute)
                if value and self_value is None:
                    self.set_attribute(attribute, value)
                elif value and self_value != value:
                    print(f"Attribute {attribute} is different in both ACDDMetadata objects")