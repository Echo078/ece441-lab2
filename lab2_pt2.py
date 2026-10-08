import numpy as np
import mne

import os
import matplotlib.pyplot as plt

import lab2_pt1

ELECTRODE_NAMES = ['FP1', 'FP2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2']
ELECTRODE_MONTAGE = {
    "FP1": np.array([-3.022797, 10.470795, 7.084885]),
    "FP2": np.array([2.276825, 10.519913, 7.147003]),
    "C3": np.array([-7.339218, -0.774994, 11.782791]),
    "C4": np.array([6.977783, -1.116196, 12.059814]),
    "P7": np.array([-7.177689, -5.466278, 3.646164]),
    "P8": np.array([7.306992, -5.374619, 3.843689]),
    "O1": np.array([-2.681717, -9.658279, 3.634674]),
    "O2": np.array([2.647095, -9.638092, 3.818619])
}

BAND_START = 1
BAND_STOP = 40


def get_eeg_as_numpy_array(data_df):
    """ Returns a numpy array of dimension (# of EEG channels) x
    (# of samples), containing only EEG channel data present in
    <data_df>. The order of the rows is in ascending numeric order
    found in the initial file ordering:

        EEG Channel 1, 2, ... (# of channels)

    data_df: a pandas dataframe, with format as defined by the return
    value of lab2_pt1.load_recording_file
    """
    # TODO: replace this with your code

    #find all columns & store in eeg_columns
    eeg_columns = []
    for col_name in data_df.columns:
        if lab2_pt1.is_eeg(col_name):
            eeg_columns.append(col_name)

    #name channel number (1, 2, 3...8)
    eeg_columns.sort(
        key=lambda name: int(
            name.replace(lab2_pt1.EEG_CHANNEL_PREFIX, "")
        )
    )

    #return (channel x sample data) -> (8, 108288)
    return np.array(data_df[eeg_columns], dtype = float).T

def construct_mne(data_df):
    """ Returns an MNE Raw object, consisting of lab2_pt1.NUM_CHANNELS
    channels of EEG data.

    data_df: a pandas dataframe, with format as defined by the return
    value of lab2_pt1.load_recording_file
    """
    # TODO: replace this with your code
    eeg_data = get_eeg_as_numpy_array(data_df) * 1e-6 #unit uV to V as per MNE requirement

    #keep electrode name, 250Hz sampling rate, EEG channels type
    info = mne.create_info(
        ch_names=ELECTRODE_NAMES,
        sfreq=lab2_pt1.SAMPLE_RATE,
        ch_types=["eeg"] * lab2_pt1.NUM_CHANNELS
    )

    data_mne = mne.io.RawArray(eeg_data, info)

    #cm -> m as per MNE requirement
    electrode_positions = {
        name: position / 100
        for name, position in ELECTRODE_MONTAGE.items()
    }

    montage = mne.channels.make_dig_montage(
        ch_pos=electrode_positions, #channel position dictrionary, 3d coordinates
        coord_frame="head"
    )


    data_mne.set_montage(montage)

    return data_mne



def show_psd(
    data_mne,
    fmin=0,
    fmax=np.inf,
    output_name="psd.png",
    output_folder="lab2part2_4567",
    title="EEG"
):
    """ Plots the power spectral density of the EEG signals in
    <data_mne>, limiting the range of the horizontal axis of the plot to
    [fmin, fmax].

    data_mne: MNE Raw object
    fmin: lower end of horizontal axis range
    fmax: upper end of horizontal axis range
    output_name: filename for the saved plot
    output_folder: subfolder inside figures for saving plots
    title: title displayed above the plot
    """
   # TODO: replace this with your code

    # Estimate PSD within the selected frequency range using Welch's method
    spectrum = data_mne.compute_psd(
        method="welch",
        fmin=fmin,
        fmax=fmax
    )

    # Plot each channel separately using colors based on electrode positions
    fig = spectrum.plot(
        average=False,
        spatial_colors=True,
        show=False
    )

    fig.suptitle(title)

    # Save plot in the selected folder
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "figures",
        output_folder
    )
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_name)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")

    plt.show()
    plt.close(fig)


def filter_band_pass(data_mne):
    """ Mutates data_mne, applying a band-pass filter
    with band defined by BAND_START and BAND_STOP, where
    BAND_START < BAND_STOP.

    data_mne: MNE Raw object
    """

    # Apply the band defined by BAND_START and BAND_STOP
    data_mne.filter(
        l_freq=BAND_START,
        h_freq=BAND_STOP
    )


def filter_notch_60(data_mne):
    """ Mutates data_mne, applying a notch filter
    to remove 60 Hz electrical noise

    data_mne: MNE Raw object
    """
    # TODO: replace this with your code
    data_mne.notch_filter(freqs=[60])


if __name__ == "__main__":
    data_df = lab2_pt1.load_recording_file("sample_data.txt")

    eeg_array = get_eeg_as_numpy_array(data_df)
    print("EEG array shape:", eeg_array.shape)

    data_mne = construct_mne(data_df)

    print("MNE data shape:", data_mne.get_data().shape)
    print("Channel names:", data_mne.ch_names)
    print("Sampling rate:", data_mne.info["sfreq"])
    print("Channel types:", data_mne.get_channel_types())
    print("First sample in volts:", data_mne.get_data()[0, 0])


    #-----plots for part 4567 for method verification
    show_psd(
        data_mne,
        fmin=0,
        fmax=125, #fs=250/2 = 125
        output_name="sample_data_raw_psd.png"
    )

    # Apply notch filtering to a copy of the original data
    data_notch = data_mne.copy()
    filter_notch_60(data_notch)

    show_psd(
        data_notch,
        fmin=0,
        fmax=125,
        output_name="sample_data_notch_psd.png"
    )

    # Apply band-pass filtering to a copy of the notched data
    data_filtered = data_notch.copy()
    filter_band_pass(data_filtered)

    show_psd(
        data_filtered,
        fmin=0,
        fmax=125,
        output_name="sample_data_notch_bandpass_psd.png"
    )

    # Part 2, Step 8: compare eyes-open and eyes-closed recordings
    recordings = [
        ("EO1", "openeye1.txt", "Eyes open"),
        ("EO2", "openeye2.txt", "Eyes open"),
        ("EO3", "openeye3.txt", "Eyes open"),
        ("EC1", "closeeye1.txt", "Eyes closed"),
        ("EC2", "closeeye2.txt", "Eyes closed"),
        ("EC3", "closeeye3.txt", "Eyes closed")
    ]

    for label, file_name, condition in recordings:
        print(f"\nProcessing {label}: {condition}")

        recording_path = os.path.join("recordings", file_name)
        recording_df = lab2_pt1.load_recording_file(recording_path)
        recording_mne = construct_mne(recording_df)

        recording_filtered = recording_mne.copy()
        filter_notch_60(recording_filtered)
        filter_band_pass(recording_filtered)

        show_psd(
            recording_filtered,
            fmin=1,
            fmax=30,
            output_name=f"{label}_all_channels_psd.png",
            output_folder="lab28",
            title=(
                f"{label} - {condition} | All channels | "
                f"Notch 60 Hz + band-pass {BAND_START}-{BAND_STOP} Hz"
            )
        )
