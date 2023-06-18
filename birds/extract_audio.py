""" For extracting the intersting parts of one audio sample """

import logging
import warnings
from pathlib import Path
from typing import Sequence, Tuple

import librosa
import numpy as np
import soundfile  # type: ignore


def find_max_index(samples: Sequence[int]) -> int:
    """Return the index of the maximum value in samples"""
    biggest = max(samples)

    return samples.index(biggest)


def surrounding_of_max_value(
    samples: Sequence[int], surrounding: int
) -> Tuple[int, int]:
    """Return a tuple of lower_index and upper_index centered around @samples
    maximum value and with @surrounding samples on either side, truncated if
    not enough samples."""
    max_index = find_max_index(samples)
    min_sample = max(0, max_index - surrounding)
    max_sample = min(len(samples) - 1, max_index + surrounding + 1)
    return min_sample, max_sample


def frame_to_ms(frame: int, framerate: int, channels: int) -> int:
    """Convert frame number to its corresponding millisecond"""
    second = float(frame) / (float(framerate) * channels)
    ms = second * 1000
    return int(ms)


def loudest_two_seconds(samples, sample_rate: int):
    """Return two seconds worth of samples with the highest power"""
    return n_with_highest_power(samples, 2 * sample_rate)[0]


def root_mean(samples):
    return np.mean(np.square(samples))


def n_with_highest_power(samples: np.ndarray, n: int) -> Tuple[np.ndarray, int]:
    """Find the n contiguous samples (window) with highest power, and where it starts

                                                   |
                                         |        ||
                                    ||  |||      ||||       |
    signal:                        |||||||||....||||||.....|||..|||..

    samples with max power (n=4):                ----
    """

    if n > samples.size:
        raise ValueError(
            f"Too few samples to extract {n} samples. ({samples.size} samples in clip"
        )
    assert n <= samples.size
    # TODO: Handle short sound clips
    if n == samples.size:
        return samples, 0

    start_of_max_window = 0
    max_power = root_mean(samples[:n])
    current_power = max_power
    for idx, (outgoing_val, incoming_val) in enumerate(
        zip(np.nditer(samples), np.nditer(samples[n:]))
    ):
        current_power -= np.divide(np.square(outgoing_val), n)
        current_power += np.divide(np.square(incoming_val), n)
        if current_power > max_power:
            max_power = current_power
            start_of_max_window = idx + 1

    return samples[start_of_max_window : start_of_max_window + n], start_of_max_window


def write_loudest_two_seconds_to_file(infile: Path, outfile: Path) -> None:
    """Extract the two loudest seconds from @infile and write it to @outfile
    as a .mp3 file"""
    # Silence warning about using audioread instead of soundfile
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        samples, sample_rate = librosa.load(infile)
    try:
        extracted_sound = loudest_two_seconds(samples, int(sample_rate))
        soundfile.write(outfile, extracted_sound, sample_rate)
    except ValueError:
        logging.warning(f"{infile} skipped because it is shorter than 2 seconds")
