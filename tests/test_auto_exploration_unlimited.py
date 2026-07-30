import unittest
from unittest.mock import Mock

from src.tasks.AutoExploration import AutoExploration


class TestAutoExplorationUnlimited(unittest.TestCase):

    def test_stop_func_does_not_stop_at_any_round(self):
        task = AutoExploration.__new__(AutoExploration)
        task.get_round_info = Mock()
        task.current_round = 999999

        result = task.stop_func()

        self.assertIsNone(result)
        task.get_round_info.assert_not_called()


if __name__ == "__main__":
    unittest.main()
