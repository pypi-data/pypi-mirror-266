import re
from classes import AnalogChannelData, DigitalChannelData
from nptdms import TdmsChannel
import numpy as np

def compileChannels(
    channels: list[TdmsChannel],
) -> tuple[dict[str, AnalogChannelData], dict[str, DigitalChannelData]]:
    toReturn_AI = {}
    toReturn_DI = {}

    for channel in channels:
        props = channel.properties
        type = props["Channel Type"]
        if "AI" in type:
            parsed_as = "AI"
            channel_data_obj = AnalogChannelData(
                rawData=channel.data,
                properties=props,
                name=props["Channel Name"],
                slope=props["Slope"],
                offset=props["Offset"],
                zeroing_target=props["Zeroing Target"],
                zeroing_correction=props["Zeroing Correction"],
                description=props["Description"],
                units=props["Unit"],
                channel_type=props["Channel Type"],
                constant_cjc=props["constant CJC"],
                tc_type=props["TC Type"],
                min_v=props["Minimum"],
                max_v=props["Maximum"],
            )
            toReturn_AI[channel_data_obj.name] = channel_data_obj
        else:
            parsed_as = "DI"
            channel_data_obj = DigitalChannelData(
                rawData=channel.data,
                properties=props,
                name=props["Channel Name"],
                channel_type=props["Channel Type"],
                description=props["Description"],
            )
            toReturn_DI[channel_data_obj.name] = channel_data_obj

        print("parsed " + channel_data_obj.name + " as " + parsed_as)
    return (toReturn_AI, toReturn_DI)


def getTime(
    channel_data: dict[str, AnalogChannelData | DigitalChannelData], group_name: str
) -> list[float]:
    samples: int = channel_data[next(iter(channel_data))].rawData.size
    pattern: str = r"\(([^()]+)\)"
    match: re.Match = re.search(pattern, group_name)
    sample_rate: float = float(match.group(1)[:-3])
    dt: float = 1 / sample_rate
    time: list[float] = np.arange(0, samples * dt, dt).tolist()
    return time
