# Purdue Space Program: Liquids BCLS DAQ utils

Used to parse, convert, pickle, and pre-process TDMS files from BCLS or other NI daq boxes.

Written in typed Python for easier linting (pref: ruff)

## Installation

To install, simply run `pip install psp-liquids-daq-parser`

## Use

There are two functions and two classes that come with this package:

### Function: `parseTDMS`:

If `file_path_custom` isn't specified, the file picker dialog comes up to select a tdms file. Then, we check to see if there's an equivalent pickle file in the same directory as the chosen tdms file.
If there's a pickle file, we parse that. Otherwise, we parse the TDMS file and save the resulting object to a pickle file for later.

### Function: `extendDatasets`

Basically makes all the datasets of all the channel the same length. Uses the numpy "edge" method for the time dataset. Uses constant values for channel data (o for analog data, 0.5 for binary data)

For example, if you had:
`    {
    "channel1": [0, 1, 2],
    "channel2": [23, 234, 235, 12, 456]
    }
   `
, this function would return:
`    {
    "channel1": [0, 1, 2, 0, 0],
    "channel2": [23, 234, 235, 12, 456]
    }
   `

### Class: `DigitalChannelData`

### Class: `AnalogChannelData`

## Matplotlib Example

Assuming you've downloaded CMS's coldflow 2 data into a folder called "cf2" and pip installed this package:

```python3.11
from psp_liquids_daq_parser import parseTDMS, extendDatasets
from matplotlib import pyplot as plt

channel_datasets = parseTDMS(5, file_path_custom="./cf2/DataLog_2024-0406-1828-28_CMS_Data_Wiring_5.tdms")

channel_datasets.update(parseTDMS(6, file_path_custom="./cf2/DataLog_2024-0406-1828-28_CMS_Data_Wiring_6.tdms"))

(available_channels, data) = extendDatasets(channel_datasets)

binary_multiplier: float = 1

PT_FU_04 = data["pt-fu-04"]
PT_HE_01 = data["pt-he-01"]
PT_OX_04 = data["pt-ox-04"]
PT_N2_01 = data["pt-n2-01"]
PT_FU_02 = data["pt-fu-02"]
PT_OX_02 = data["pt-ox-02"]
TC_OX_04 = data["tc-ox-04"]
TC_FU_04 = data["tc-fu-04"]
TC_OX_02 = data["tc-ox-02"]
TC_FU_02 = data["tc-fu-02"]
RTD_FU = data["rtd-fu"]
RTD_OX = data["rtd-ox"]
PT_FU_202 = data["pt-fu-202"]
PT_HE_201 = data["pt-he-201"]
PT_OX_202 = data["pt-ox-202"]
PT_TEST_AI_20 = data["pt-test-ai-20"]
PI_HE_01 = data["pi-he-01"] * binary_multiplier
PI_FU_02 = data["pi-fu-02"] * binary_multiplier
PI_OX_02 = data["pi-ox-02"] * binary_multiplier
PI_FU_03 = data["pi-fu-03"] * binary_multiplier
PI_OX_03 = data["pi-ox-03"] * binary_multiplier
REED_BP_01 = data["reed-bp-01"] * binary_multiplier
PI_FU_201 = data["pi-fu-201"] * binary_multiplier
PI_OX_201 = data["pi-ox-201"] * binary_multiplier
REED_MAROTTA_1 = data["reed-marotta-1"] * binary_multiplier
REED_MAROTTA_2 = data["reed-marotta-2"] * binary_multiplier
REED_N2_02 = data["reed-n2-02"] * binary_multiplier
REED_MAROTTA_3 = data["reed-marotta-3"] * binary_multiplier
TC_OX_201 = data["tc-ox-201"]
TC_FU_201 = data["tc-fu-201"]
time: list[float] = data["time"]

fig, host = plt.subplots()
ax1 = host.twinx()
host.plot(time, PT_FU_202)
ax1.plot(time, REED_MAROTTA_1)
host.set_xlabel("time (s)")
host.set_ylabel("pressure (psi)")
ax1.set_ylabel("binary")

fig, host = plt.subplots()
ax1 = host.twinx()
host.plot(time, PT_OX_202)
ax1.plot(time, REED_MAROTTA_2)
plt.show()

```

## Plotly Example

Assuming you've downloaded CMS's coldflow 2 data into a folder called "cf2" and pip installed both this package and `dash`:

```python3.11
from psp_liquids_daq_parser import extendDatasets, parseTDMS

from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

# Use the tdms file's functions to get multiple tdms files, then combine them
channel_data = parseTDMS(
    5,
    file_path_custom="./cf2/DataLog_2024-0406-1828-28_CMS_Data_Wiring_5.tdms",  # the "file_path_custom" arg is optional
)
channel_data.update(
    parseTDMS(
        6,
        file_path_custom="./cf2/DataLog_2024-0406-1828-28_CMS_Data_Wiring_6.tdms",
    )
)
# after combining, make all the datasets the same length by extending the datasets if necessary
available_channels, df_list_constant = extendDatasets(channel_data)


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            children="Coldflow 2 Data",
            style={"textAlign": "center", "fontFamily": "sans-serif"},
        ),
        html.I("scale PI/binary data by: "),
        dcc.Input(
            id="input_{}".format("number"),
            type="number",
            placeholder="input type {}".format("number"),
            debounce=True,
            value=5000,
        ),
        dcc.Graph(id="graph-content", style={"width": "95vw", "height": "85vh"}),
    ]
)


# This is called whenver input is submitted (usually by the user clicking out of the input box), and re-draws the UI
@callback(Output("graph-content", "figure"), Input("input_number", "value"))
def update_graph(value):
    binary_multiplier: float = float(value)
    print(available_channels)
    df_list = {}
    df_list.update(df_list_constant)

    for channel in available_channels:
        if "reed-" in channel or "pi-" in channel:
            df_list.update(
                {
                    channel: df_list[channel] * binary_multiplier,
                }
            )
    df = pd.DataFrame.from_dict(df_list)
    fig = px.line(df, x="time", y=df.columns[0:-1])
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="80")

```
