import wave

from typing import List

import numpy


def wav_to_frames(wav_file: str) -> List[int]:
    " open a .wav file and convert it to a list of samples "
    wav = wave.open(wav_file, "rb")
    return numpy.frombuffer(wav.readframes(-1), numpy.int16)


def absolute_fft(signal):
    " Do a discrete fft on @signal and return the absolute value "
    return numpy.absolute(numpy.fft.rfft(signal))


if __name__ == "__main__":
    pass
