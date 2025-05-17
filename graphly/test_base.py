import pytest
from .base import RootNode, DSData, RootData


class DemoOutput(RootData):
    def __init__(self):
        pass


class DemoNode(RootNode):
    def process(self, input_data: DSData) -> DemoOutput:
        return DemoOutput()


@pytest.mark.xfail(raises=RuntimeError)
class TestBase:
    def test_root_data(self):
        do = DSData()
        do._get_data_types()
        do._validate_data({"raw_temperature": 34, "mac_address": 'b33f', "invalid": True})
        assert False