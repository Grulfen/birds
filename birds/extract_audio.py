""" For extracting the intersting parts of one audio sample """

from typing import Sequence, Tuple
from pydub import AudioSegment
import io


def find_max_index(samples: Sequence[int]) -> int:
    """ Return the index of the maximum value in samples """
    biggest = max(samples)

    return samples.index(biggest)


def surrounding_of_max_value(samples: Sequence[int],
                             surrounding: int) -> Tuple[int, int]:
    """ Return a tuple of lower_index and upper_index centered around @samples
    maximum value and with @surrounding samples on either side, truncated if
    not enough samples."""
    max_index = find_max_index(samples)
    min_sample = max(0, max_index - surrounding)
    max_sample = min(len(samples) - 1, max_index + surrounding + 1)
    return min_sample, max_sample


def frame_to_ms(frame: int, framerate: int, channels: int) -> int:
    """ Convert frame number to its corresponding millisecond """
    second = float(frame) / (float(framerate) * channels)
    ms = second * 1000
    return int(ms)


def loudest_two_seconds(segment: AudioSegment) -> AudioSegment:
    """ Return a two second AudioSegment centered around the loudest sample """
    # samples: list of frames
    samples = segment.get_array_of_samples()

    # frames_in_sec : frames/sec
    frames_in_sec = segment.frame_rate * segment.channels

    lower_idx, upper_idx = surrounding_of_max_value(samples, frames_in_sec)

    # lower_idx, upper_idx : s
    lower_idx = frame_to_ms(lower_idx, segment.frame_rate, segment.channels)
    upper_idx = frame_to_ms(upper_idx, segment.frame_rate, segment.channels)

    assert lower_idx < len(segment), (
        "lower sample ({}) should be which ms "
        "to start the audio from").format(lower_idx)
    assert upper_idx < len(segment), (
        "upper sample ({}) should be which ms "
        "to stop the audio from").format(upper_idx)

    return segment[lower_idx: upper_idx]


# TODO: Make this return io.BytesIO or something
# TODO: Use part of sound with highest energy or something instead
def extract_two_loudest_seconds(infile: io.BytesIO, outfile: str):
    """ Extract the two loudest seconds from @infile and write it to @outfile
    as a .mp3 file """
    sound = AudioSegment.from_mp3(infile)
    extracted_sound = loudest_two_seconds(sound)
    extracted_sound.export(outfile, format="mp3")
