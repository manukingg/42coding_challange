from challenges.easy.two_sum.solution import two_sum


def test_two_sum_example_1() -> None:
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]


def test_two_sum_example_2() -> None:
    assert two_sum([3, 2, 4], 6) == [1, 2]


def test_two_sum_example_3() -> None:
    assert two_sum([3, 3], 6) == [0, 1]


def test_two_sum_handles_negative_numbers() -> None:
    assert two_sum([-3, 4, 3, 90], 0) == [0, 2]


def test_two_sum_handles_zero() -> None:
    assert two_sum([0, 4, 3, 0], 0) == [0, 3]
