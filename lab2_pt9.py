"""Compare four electrode pairs across six recordings for Part 2, Step 9."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Save all plots without opening interactive windows.
import matplotlib.pyplot as plt
import numpy as np

import lab2_pt1
import lab2_pt2


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "figures" / "lab29"
BAND_START, BAND_STOP = 1, 40
FMIN, FMAX = 5, 20

RECORDINGS = [
    ("EO1", "openeye1.txt", "Eyes open"),
    ("EO2", "openeye2.txt", "Eyes open"),
    ("EO3", "openeye3.txt", "Eyes open"),
    ("EC1", "closeeye1.txt", "Eyes closed"),
    ("EC2", "closeeye2.txt", "Eyes closed"),
    ("EC3", "closeeye3.txt", "Eyes closed"),
]

CHANNEL_GROUPS = {
    # Frontal poles: inspect frontal activity and possible eye-related artifacts.
    "Frontal poles": ["FP1", "FP2"],
    # Central sites: compare rhythms near the sensorimotor regions.
    "Central": ["C3", "C4"],
    # Parietal sites: inspect posterior activity outside the occipital pair.
    "Parietal": ["P7", "P8"],
    # Occipital sites: look for alpha changes between eyes-open and closed trials.
    "Occipital": ["O1", "O2"],
}


def draw_pair(ax, spectrum, channels, title, ylim):
    """Draw the same channel-pair comparison on any subplot."""
    power, frequencies = spectrum.get_data(picks=channels, return_freqs=True)
    power_db = 10 * np.log10(power * 1e12)  # Convert V²/Hz to dB re 1 µV²/Hz.

    # Use blue for the left channel and red for the right channel in every pair.
    for channel, values, color in zip(channels, power_db, ["#2166ac", "#d6604d"]):
        ax.plot(frequencies, values, color=color, label=channel, linewidth=1.2)

    # Highlight the alpha range and mark 10 Hz without changing the data.
    ax.axvspan(8, 13, color="gray", alpha=0.12, label="Alpha range (8-13 Hz)")
    ax.axvline(10, color="gray", linestyle="--", linewidth=0.8)
    ax.set(
        title=title,
        xlim=(FMIN, FMAX),
        ylim=ylim,
    )
    ax.set_xticks([5, 8, 10, 13, 15, 20])
    ax.grid(alpha=0.25)


def plot_pair(spectrum, channels, title, output_path, ylim):
    """Save one channel-pair PSD with clear labels and shared axis limits."""
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
    draw_pair(ax, spectrum, channels, title, ylim)
    ax.set(xlabel="Frequency (Hz)", ylabel="PSD (dB re 1 µV²/Hz)")
    ax.legend(loc="upper right")
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path.relative_to(PROJECT_DIR)}")


def plot_pair_comparison(spectra, channels, region, output_path, ylim):
    """Compare all six recordings for one electrode pair in a 3-by-2 grid."""
    fig, axes = plt.subplots(
        3, 2, figsize=(13, 11), sharex=True, sharey=True, layout="constrained"
    )
    # Left column: eyes open. Right column: eyes closed. Rows: trials 1-3.
    for label, filename, condition, spectrum in spectra:
        row = int(label[-1]) - 1
        column = 0 if label.startswith("EO") else 1
        draw_pair(axes[row, column], spectrum, channels, f"{label} - {condition}", ylim)

    # Shared axes, colors, and legend make comparisons consistent across trials.
    fig.suptitle(
        f"{region}: {', '.join(channels)} | Six-recording comparison\n"
        f"60 Hz notch + {BAND_START}-{BAND_STOP} Hz band-pass | Full recordings"
    )
    for ax in axes[-1]:
        ax.set_xlabel("Frequency (Hz)")
    fig.supylabel("PSD (dB re 1 µV²/Hz)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    spectra = []
    for label, filename, condition in RECORDINGS:
        print(f"\nProcessing {label}: {condition}")
        path = PROJECT_DIR / "data" / "recordings" / filename
        data_df = lab2_pt1.load_recording_file(str(path))
        data_mne = lab2_pt2.construct_mne(data_df)

        # Apply identical filters to all six full recordings before estimating PSD.
        lab2_pt2.filter_notch_60(data_mne)
        data_mne.filter(l_freq=BAND_START, h_freq=BAND_STOP)
        spectrum = data_mne.compute_psd(method="welch", fmin=FMIN, fmax=FMAX)
        spectra.append((label, filename, condition, spectrum))

    # Find one vertical scale that covers all channels and all six recordings.
    all_db = [10 * np.log10(s.get_data() * 1e12) for _, _, _, s in spectra]
    lower = 5 * np.floor(min(values.min() for values in all_db) / 5) - 5
    upper = 5 * np.ceil(max(values.max() for values in all_db) / 5) + 5
    ylim = (lower, upper)

    for label, filename, condition, spectrum in spectra:
        folder = OUTPUT_DIR / Path(filename).stem
        folder.mkdir(parents=True, exist_ok=True)
        for region, channels in CHANNEL_GROUPS.items():
            title = (
                f"{label} - {condition} | {region}: {', '.join(channels)}\n"
                f"60 Hz notch + {BAND_START}-{BAND_STOP} Hz band-pass | Full recording"
            )
            output_path = folder / f"{label}_{'_'.join(channels)}_psd.png"
            plot_pair(spectrum, channels, title, output_path, ylim)

    # Save one six-panel summary for each region alongside the individual plots.
    comparison_folder = OUTPUT_DIR / "comparisons"
    comparison_folder.mkdir(parents=True, exist_ok=True)
    for region, channels in CHANNEL_GROUPS.items():
        output_path = comparison_folder / f"{'_'.join(channels)}_six_recordings.png"
        plot_pair_comparison(spectra, channels, region, output_path, ylim)

    print("\nFinished: 24 individual plots and four six-recording comparisons.")
