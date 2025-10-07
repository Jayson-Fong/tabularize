"""
Tests for utility functions
"""

import random

# noinspection PyProtectedMember
import tabularize._util as util


def test_find_any() -> None:
    """
    Test find functions against baseline to determine if indexes are correct.

    :return: None.
    """

    for baseline_func_name, test_func, comparison_func in (
        ("find", util.find_any, min),
        ("rfind", util.rfind_any, max),
    ):
        for _ in range(128):
            data = random.randbytes(random.randint(1, 128))
            baseline_func = getattr(data, baseline_func_name)

            # Single Search
            find_byte: bytes = random.randbytes(1)
            assert baseline_func(find_byte) == test_func(data, (find_byte[0],))

            # Single Search with Manual End
            end_index = random.randint(0, len(data))
            assert baseline_func(find_byte, 0, end_index) == test_func(
                data, (find_byte[0],), 0, end_index
            )

            # Double Search
            find_byte_1, find_byte_2 = random.randbytes(1), random.randbytes(1)
            found_byte_1, found_byte_2 = baseline_func(find_byte_1), baseline_func(
                find_byte_2
            )

            if found_byte_1 != -1 and found_byte_2 == -1:
                baseline: int = found_byte_1
            elif found_byte_2 != -1 and found_byte_1 == -1:
                baseline: int = found_byte_2
            else:
                baseline: int = comparison_func(found_byte_1, found_byte_2)

            assert baseline == test_func(data, (find_byte_1[0], find_byte_2[0]))
