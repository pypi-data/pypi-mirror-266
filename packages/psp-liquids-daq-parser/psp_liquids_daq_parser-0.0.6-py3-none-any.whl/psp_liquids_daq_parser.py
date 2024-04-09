from nptdms import TdmsFile, TdmsGroup
import pickle
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
from classes import AnalogChannelData, DigitalChannelData
from helpers import compileChannels, getTime

def parseTDMS(
    dev_num: int, file_path_custom: str = "", dev_group: str = "Data (1000.000000 Hz)"
) -> dict[str, AnalogChannelData | DigitalChannelData | list[float]]:
    """## Parse a TDMS file (or an equivalent pickle file)
    ### Arguments:
    - `dev_num` (Type: `int`): dev box number (i.e: the `5` or `6` in dev5 or dev6)
    - (Optional) `file_path_custom` (Type: `str`): the dynamic file path to a `.TDMS` file (use this in case you don't want to keep selecting the tdms file to parse every time you run the script)
    - (Optional) `dev_group` (Type: `str`): the TDMS group header. You usually don't have to touch this unless the data isn't high frequency sampling data
    ### Description
    If `file_path_custom` isn't specified, the file picker dialog comes up to select a tdms file. Then, we check to see if there's an equivalent pickle file in the same directory as the chosen tdms file.
    If there's a pickle file, we parse that. Otherwise, we parse the TDMS file and save the resulting object to a pickle file for later.
    """
    if file_path_custom == "":
        root = tk.Tk()
        root.withdraw()
        filepath: str = filedialog.askopenfilename(
            initialdir="./", title="Choose Dev" + str(dev_num) + " TDMS file"
        )
        print(
            f'to skip the filepicker, use "parseTDMS({dev_num}, file_path_custom={filepath})"'
        )
    else:
        filepath = file_path_custom
    pickle_filepath: str = filepath[:-5] + ".pickle"
    if os.path.exists(pickle_filepath):
        print("unpickling...")
        with open(pickle_filepath, "rb") as f:
            unpickledData: dict[
                str, AnalogChannelData | DigitalChannelData | list[float]
            ] = pickle.loads(f.read())
            print("unpickled data")
            return unpickledData
    else:
        channel_data_map: dict[
            str, AnalogChannelData | DigitalChannelData | list[float]
        ] = {}
        tdms_file: TdmsFile = TdmsFile.read(filepath)
        group: TdmsGroup = tdms_file[dev_group]
        dev5_channels = compileChannels(group.channels())
        channel_data_map.update(dev5_channels[0])
        channel_data_map.update(dev5_channels[1])
        channel_data_map["time"] = getTime(channel_data_map, dev_group)
        with open(pickle_filepath, "wb") as f:
            pickle.dump(channel_data_map, f, pickle.HIGHEST_PROTOCOL)
        print(
            f'conversion done!\n\n\nNext time you want to run the converter, consider calling the function with: "parseTDMS({dev_num}, file_path_custom={pickle_filepath[:-7] + ".tdms"})"'
        )
        return channel_data_map

def extendDatasets(
    channel_data: dict[str, AnalogChannelData | DigitalChannelData | list[float]], binary_channel_prefixes: tuple[str] = ("pi-", "reed-")
) -> tuple[list[str], dict[str, AnalogChannelData | DigitalChannelData | list[float]]]:
    """## Extend combined datasets
    Basically makes all the datasets of all the channel the same length. Uses the numpy "edge" method for the time dataset. Uses constant values for channel data (o for analog data, 0.5 for binary data)

    For example, if you had:
    ```
    {
    "channel1": [0, 1, 2],
    "channel2": [23, 234, 235, 12, 456]
    }
    ```
    this function would return:
    ```
    {
    "channel1": [0, 1, 2, 0, 0],
    "channel2": [23, 234, 235, 12, 456]
    }
    ```

    ### Arguments
    - `channel_data` (Type: `dict[str, AnalogChannelData | DigitalChannelData | list[float]]`): the output of `parseTDMS` or multiple `parseTDMS`s
    - (Optional) `binary_channel_prefixes` (Type: `tuple[str]`): The channel name prefixes that indicate if the channel is a binary output channel
    ### Outputs (`tuple`)
    - `list[str]`: the list of all channel names that were provided
    - `dict[str, AnalogChannelData | DigitalChannelData | list[float]]`: the extended data in the same format as outputted by `parseTDMS`
    """
    # get all the available channel names
    available_channels = list(channel_data.keys())

    # get the length of the largest dataset
    total_length: int = 0
    for channel in available_channels:
        if channel != "time" and len(channel_data[channel].data) > total_length:
            total_length = len(channel_data[channel].data)

    # for each channel, pad the end of that channel's dataset with some value to
    # make all the channel's data the same length and simeltaneously convert it all to np arrays
    df_list_constant = {}
    time: list[float] = channel_data["time"]
    df_list_constant.update(
        {"time": np.pad(time, (0, total_length - len(time)), "edge")}
    )
    for channel in available_channels:
        # for binary channels, make the padding value 0.5 to make it easy to identify which data is to be ignored
        if channel.startswith(binary_channel_prefixes):
            df_list_constant.update(
                {
                    channel: np.pad(
                        channel_data[channel].data,
                        (0, total_length - len(channel_data[channel].data)),
                        "constant",
                        constant_values=(
                            0.5,
                            0.5,
                        ),
                    )
                }
            )
        # for all other channels, set the padding value to zero
        elif channel != "time":
            df_list_constant.update(
                {
                    channel: np.pad(
                        channel_data[channel].data,
                        (0, total_length - len(channel_data[channel].data)),
                        "constant",
                        constant_values=(0, 0),
                    )
                }
            )

    return (available_channels, df_list_constant)
