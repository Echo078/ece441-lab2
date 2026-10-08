"""Save three full-recording PSD stages for each of the six EEG recordings.

The reference band is 0.1-120 Hz, using MNE's default FIR filter. Its
approximately 33-second filter is longer than these recordings, so MNE
warns about possible distortion. Treat this as a limitation of these
reference plots. The Step 8 script continues to use its own 1-40 Hz band.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Save images without opening interactive windows.
import matplotlib.pyplot as plt

import lab2_pt1
import lab2_pt2


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "figures" / "lab28_reference"
BAND_START = 0.1
BAND_STOP = 120

RECORDINGS = [
    ("EO1", "openeye1.txt", "Eyes open"),
    ("EO2", "openeye2.txt", "Eyes open"),
    ("EO3", "openeye3.txt", "Eyes open"),
    ("EC1", "closeeye1.txt", "Eyes closed"),
    ("EC2", "closeeye2.txt", "Eyes closed"),
    ("EC3", "closeeye3.txt", "Eyes closed"),
]


def save_reference_plots(data_raw, label, condition, output_dir):
    """Save raw, notch-only, and notch-plus-band-pass PSDs on matching axes."""
    data_notch = data_raw.copy()
    lab2_pt2.filter_notch_60(data_notch)

    data_bandpass = data_notch.copy()
    data_bandpass.filter(l_freq=BAND_START, h_freq=BAND_STOP)

    stages = [
        (data_raw, "01_raw_psd.png", "Raw - no filtering"),
        (data_notch, "02_notch60_psd.png", "60 Hz notch"),
        (
            data_bandpass,
            "03_notch60_bandpass_0p1_120_psd.png",
            f"60 Hz notch + {BAND_START}-{BAND_STOP} Hz band-pass",
        ),
    ]

    plots = []
    for data, filename, stage_title in stages:
        spectrum = data.compute_psd(
            method="welch", fmin=0, fmax=lab2_pt1.SAMPLE_RATE / 2
        )
        fig = spectrum.plot(average=False, spatial_colors=True, show=False)
        fig.suptitle(f"{label} - {condition} | {stage_title}", fontsize=12)
        plots.append((fig, filename))

    # Match the vertical scale across the three stages of this recording.
    lower = min(fig.axes[0].get_ylim()[0] for fig, _ in plots)
    upper = max(fig.axes[0].get_ylim()[1] for fig, _ in plots)
    output_dir.mkdir(parents=True, exist_ok=True)

    for fig, filename in plots:
        fig.axes[0].set_ylim(lower, upper)
        fig.axes[0].set_xlim(0, lab2_pt1.SAMPLE_RATE / 2)
        output_path = output_dir / filename
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved: {output_path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    for label, filename, condition in RECORDINGS:
        print(f"\nProcessing {label}: {filename}")
        recording_path = PROJECT_DIR / "data" / "recordings" / filename
        data_df = lab2_pt1.load_recording_file(str(recording_path))
        data_raw = lab2_pt2.construct_mne(data_df)
        save_reference_plots(data_raw, label, condition, OUTPUT_DIR / Path(filename).stem)

    print("\nFinished: six recording folders, three reference plots each.")
