import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import os
import lab2_utils as utils

##########################################################
#  Defined constants used to load in the .txt EEG files  #
##########################################################

NUM_ROWS_TO_SKIP = 4  # header data in the .txt file
NUM_CHANNELS = 8  # number of EEG channels
EEG_CHANNEL_PREFIX = utils.NEW_EEG_CHANNEL_PREFIX  # label to help us identify columns with EEG data
SAMPLE_RATE = 250  # Sampling rate of data in Hz

DATA_DIR = "data"  # directory containing recording files to be loaded and plotted
TIMESTAMP_STR = "timestamp"  # name of column with recording timestamps

# Used to plot EEG channels in the same colors as shown on the
# OpenBCI GUI (and also matching the wire colors connected to
# each electrode). Keys are the EEG channel, values are the hex
# code for the corresponding color.
EEG_CHANNEL_COLORS = {
    "1": "#878787",  # gray
    "2": "#a670db",  # purple
    "3": "#697de0",  # blue
    "4": "#6be069",  # green
    "5": "#e6de4e",  # yellow
    "6": "#e6954e",  # orange
    "7": "#eb4444",  # red
    "8": "#703d1f",  # brown
}


###########################################################
#  Functions to load and plot EEG data                    #
###########################################################


def load_recording_file(fname):
    """Returns a pandas dataframe that consists of all the timeseries
    data, with associated column names, from an OpenBCI GUI recording file.
    The filename of the recording file is given by <fname>.

    fname: string representing the name of the recording file to load
    """
    file_path = os.path.join(DATA_DIR, fname)
    data_df = pd.read_csv(file_path, skiprows = NUM_ROWS_TO_SKIP) # TODO: your code here

    utils.clean_eeg_dataframe(data_df)  # does some cleanup
    return data_df


def is_eeg(col_name):
    """ Returns True if the column given by <col_name> contains EEG data, and
    False otherwise.

    col_name: a string representing a column in the dataframe loaded using
    load_recording_file
    """
    return col_name.startswith(EEG_CHANNEL_PREFIX)  # TODO: your code here


def plot_eeg_data(data_df, output_name="sample_data_eeg.png"): #save png to folder
    """ Plots all EEG channel data found in the pandas dataframe
    <data_df>.

    data_df: a Pandas dataframe consisting of EEG data to be plot
    """
    # creates 8 rows and 1 column of subplots
    fig, ax = plt.subplots(
        NUM_CHANNELS, 1, sharex='all', figsize=(15, 15)
    )

    # iterates through columns in the dataframe 
    timestamps = data_df[TIMESTAMP_STR] # TODO: your code here
    for col_name in data_df.columns.values:
        # TODO: your code here
        # plot EEG channel 1 on the first subplot, and so on
        if is_eeg(col_name):
            channel_number = col_name.replace(EEG_CHANNEL_PREFIX, "")
            subplot_index = int(channel_number)-1

            ax[subplot_index].plot(
                timestamps,
                data_df[col_name],
                color=EEG_CHANNEL_COLORS[channel_number],
                label = f"EEG Channel {channel_number}"

            )

        pass


    # Adding title, legends, and axes labels
    [ax[i].legend(loc="lower left", fontsize=18) for i in range(NUM_CHANNELS)]
    fig.suptitle("EEG data over time", fontsize=22)
    fig.subplots_adjust(top=0.95, bottom=0.05)
    plt.xlabel("Time (DD HH:MM:SS)", fontsize=20)
    fig.text(0.06, 0.5, 'Recorded Signal (uV)', va='center', rotation='vertical', fontsize=20)

    # save .png to project folder, dpi=200 (clearity)
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "figures"
    )
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_name)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    recording_files = [
        "openeye1.txt",
        "openeye2.txt",
        "openeye3.txt",
        "closeeye1.txt",
        "closeeye2.txt",
        "closeeye3.txt"
    ]

    for file_name in recording_files:
        recording_path = os.path.join("recordings", file_name)
        data_df = load_recording_file(recording_path)

        output_name = file_name.replace(".txt", "_eeg.png")

        print(f"Recording: {file_name}")
        print(f"Data shape: {data_df.shape}")
        print(f"Duration: {len(data_df) / SAMPLE_RATE:.2f} seconds")

        plot_eeg_data(data_df, output_name=output_name)