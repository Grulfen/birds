""" Tests for audio extraction """
import numpy as np
from hypothesis import given
from hypothesis import strategies as st
from pytest import raises

from birds import extract_audio

# pylint:disable=no-self-use,missing-docstring,invalid-name


class TestFindMaxIndex:
    def test_returns_biggest_index(self):
        assert extract_audio.find_max_index([0, 2, 1]) == 1

    def test_raises_on_empty_list(self):
        with raises(ValueError):
            assert extract_audio.find_max_index([])


class TestSurroundingOfMaxValue:
    def test_basic(self):
        surrounding = extract_audio.surrounding_of_max_value([0, 1, 2, 1, 0], 1)
        assert surrounding == (1, 4)

    def test_empty_list(self):
        with raises(ValueError):
            extract_audio.surrounding_of_max_value([], 2)

    def test_truncates_front_if_surrounding_too_big(self):
        surrounding = extract_audio.surrounding_of_max_value([0, 3, 2, -2, -1], 2)
        assert surrounding == (0, 4)

    def test_truncates_back_if_surrounding_too_big(self):
        surrounding = extract_audio.surrounding_of_max_value([0, 3, 2, 7, -1], 2)
        assert surrounding == (1, 4)

    def test_truncates_both_if_surrounding_too_big(self):
        surrounding = extract_audio.surrounding_of_max_value([0, 3, 2], 7)
        assert surrounding == (0, 2)

    def test_returns_only_max_if_surrounding_is_zero(self):
        surrounding = extract_audio.surrounding_of_max_value([0, 3, 2], 0)
        assert surrounding == (1, 2)


class TestFrameToMs:
    def test_one_channel(self):
        assert extract_audio.frame_to_ms(100, framerate=100, channels=1) == 1000
        assert extract_audio.frame_to_ms(10, framerate=100, channels=1) == 100

    def test_two_channels(self):
        assert extract_audio.frame_to_ms(100, framerate=100, channels=2) == 500
        assert extract_audio.frame_to_ms(10, framerate=100, channels=2) == 50


@st.composite
def list_and_window_size(draw):
    lst = draw(st.lists(st.integers(min_value=0, max_value=255), min_size=4))
    window_size = draw(st.integers(min_value=1, max_value=len(lst)))
    return np.array(lst), window_size


def is_sublist_of(lst1, lst2):
    string_lst1 = " ".join(str(e) for e in lst1)
    string_lst2 = " ".join(str(e) for e in lst2)
    return string_lst1 in string_lst2


class TestLoudestInterval:
    def test_find_loudest(self):
        assert np.array_equal(
            extract_audio.n_with_highest_power(
                np.array([0, 1, 10, 11, 12, 2, 4, 3, 2]), 3
            ),
            [10, 11, 12],
        )

    @given(list_and_window_size())
    def test_n_with_highest_power_has_n_items(self, lst_and_n):
        lst, n = lst_and_n
        assert extract_audio.n_with_highest_power(lst, n).size == n
