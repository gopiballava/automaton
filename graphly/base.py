
class RootData:
    def serialize_to_json(self) -> str:
        pass
    def deserialize_from_json(self, body: str):
        pass

    def _get_data_types(self) -> dict:
        print(f"self.__dict__: {self.__dict__}")
        print(self.__class__.__annotations__)
        print(dir(self.__class__))
        return self.__class__.__annotations__
    
    def _validate_data(self, data: dict) -> bool:
        if data.keys() != self.__annotations__.keys():
            raise RuntimeError(f"Some keys are missing: data had {data.keys()}; we expected {self.__annotations__.keys()}")


class DSData(RootData):
    raw_temperature: int
    mac_address: str


class TemperatureData(RootData):
    pass

class RootNode:
    def __init__(self, root: str, **kwargs):
        pass

    def mqtt_subscribe(self):
        pass