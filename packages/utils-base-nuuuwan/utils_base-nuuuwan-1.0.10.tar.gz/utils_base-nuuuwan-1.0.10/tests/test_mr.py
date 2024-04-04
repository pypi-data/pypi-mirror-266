"""Test."""
import unittest

from utils_base import Parallel


class TestMR(unittest.TestCase):
    """Test."""

    def test_map_parallel(self):
        """Test."""

        def func_map(x):
            return x**3

        input_list = list(range(0, 10))
        expected_output = list(
            map(
                func_map,
                input_list,
            )
        )
        actual_output = Parallel.map(
            func_map,
            input_list,
            max_threads=4,
        )
        self.assertEqual(
            expected_output,
            actual_output,
        )
