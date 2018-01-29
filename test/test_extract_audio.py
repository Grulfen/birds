from birds import extract_audio

from pytest import raises

# pylint:disable=no-self-use,missing-docstring,invalid-name


class TestFindMaxIndex:

    def test_returns_biggest_index(self):
        assert extract_audio.find_max_index([0, 2, 1]) == 1

    def test_raises_on_empty_list(self):
        with raises(ValueError):
            assert extract_audio.find_max_index([])


class TestSurroundingOfMaxValue:

    def test_basic(self):
        surrounding = extract_audio.surrounding_of_max_value(
            [0, 1, 2, 1, 0], 1)
        assert surrounding == (1, 4)

    def test_empty_list(self):
        with raises(ValueError):
            extract_audio.surrounding_of_max_value([], 2)

    def test_truncates_front_if_surrounding_too_big(self):
        surrounding = extract_audio.surrounding_of_max_value(
            [0, 3, 2, -2, -1], 2)
        assert surrounding == (0, 4)

    def test_truncates_back_if_surrounding_too_big(self):
        surrounding = extract_audio.surrounding_of_max_value(
            [0, 3, 2, 7, -1], 2)
        assert surrounding == (1, 5)

    def test_truncates_both_if_surrounding_too_big(self):
        surrounding = extract_audio.surrounding_of_max_value(
            [0, 3, 2], 7)
        assert surrounding == (0, 3)

    def test_returns_only_max_if_surrounding_is_zero(self):
        surrounding = extract_audio.surrounding_of_max_value(
            [0, 3, 2], 0)
        assert surrounding == (1, 2)
