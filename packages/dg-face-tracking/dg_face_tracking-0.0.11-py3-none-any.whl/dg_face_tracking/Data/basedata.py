from copy import deepcopy
from typing import Set, Any

class BaseData:
    def __init__(self) -> None:
        self.data_type: str = ""
        self.properties: dict = dict()

    def set_data_type(self, data_type: str):
        self.data_type = data_type
    def get_data_type(self) -> str:
        return self.data_type

    def add_property(self, property_name: str, data: Any) -> None:
        self.properties[property_name] = data

    def get_property(self, property_name: str, default: Any = None) -> Any:
        return self.properties[property_name] if property_name in self.properties else default

    def del_property(self, property_name) -> None:
        if property_name in self.properties:
            del self.properties[property_name]

    def pop_property(self, property_name: str) -> Any:
        prop = None
        if property_name in self.properties:
            prop = self.properties[property_name]
            del self.properties[property_name]
        return prop

    def copy_data(self, data, excluding: Set[str] = None) -> None:
        if excluding is None:
            excluding = {}
        for key in data.properties.keys() - excluding:
            self.add_property(key, data.get_property(key))


class PoisonPill(BaseData):
    def __init__(self):
        super(BaseData, self).__init__()
        self.set_data_type("poison_pill")


