from typing import OrderedDict
from numpy import float64
from numpy.typing import NDArray

class DigitalChannelData:
    def __init__(
        self,
        rawData: NDArray[float64],
        properties: OrderedDict,
        name: str,
        description: str,
        channel_type: str,
    ):
        self._rawData = rawData
        self._properties = properties
        self._name = name
        self._channel_type = channel_type
        self._description = description

    @property
    def data(self) -> NDArray[float64]:
        return self._rawData

    @property
    def properties(self) -> OrderedDict:
        return self._properties

    @property
    def name(self) -> str:
        return self._name

    @property
    def channelType(self) -> str:
        return self._channel_type

    @property
    def description(self) -> str:
        return self._description


class AnalogChannelData:
    def __init__(
        self,
        rawData: NDArray[float64],
        properties: OrderedDict,
        name: str,
        slope: float,
        offset: float,
        zeroing_target: float,
        zeroing_correction: float,
        description: str,
        units: str,
        channel_type: str,
        constant_cjc: float,
        tc_type: str,
        min_v: float,
        max_v: float,
    ):
        self._rawData = rawData
        self._properties = properties
        self._name = name
        self._slope = slope
        self._offset = offset
        self._zeroing_target = zeroing_target
        self._zeroing_correction = zeroing_correction
        self._description = description
        self._units = units
        self._channel_type = channel_type
        self._tc_type = tc_type
        self._constant_cjc = constant_cjc
        self._min_v = min_v
        self._max_v = max_v

    @property
    def rawData(self) -> NDArray[float64]:
        return self._rawData

    @property
    def data(self) -> NDArray[float64]:
        return (self._rawData * self._slope) + self._zeroing_correction + self._offset

    @property
    def properties(self) -> OrderedDict:
        return self._properties

    @property
    def name(self) -> str:
        return self._name

    @property
    def slope(self) -> float:
        return self._slope

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def zeroing_target(self) -> float:
        return self._zeroing_target

    @property
    def zeroing_correction(self) -> float:
        return self._zeroing_correction

    @property
    def description(self) -> str:
        return self._description

    @property
    def units(self) -> str:
        return self._units

    @property
    def channelType(self) -> str:
        return self._channel_type

    @property
    def constant_cjc(self) -> float:
        return self._constant_cjc

    @property
    def tc_type(self) -> str:
        return self._tc_type

    @property
    def min_v(self) -> float:
        return self._min_v

    @property
    def max_v(self) -> float:
        return self._max_v
