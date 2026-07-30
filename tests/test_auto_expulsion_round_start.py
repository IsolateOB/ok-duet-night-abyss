import unittest
from unittest.mock import Mock

from src.tasks.AutoExpulsion import AutoExpulsion
from src.tasks.CommissionsTask import Mission


class EndIteration(Exception):
    pass


class TestAutoExpulsionRoundStart(unittest.TestCase):

    def make_task(self, status):
        task = AutoExpulsion.__new__(AutoExpulsion)
        calls = Mock()
        task.init_all = calls.init_all
        task.load_char = calls.load_char

        def handle_mission_interface(**kwargs):
            calls.handle_mission_interface()
            return status

        task.handle_mission_interface = Mock(side_effect=handle_mission_interface)
        task.wait_until = calls.wait_until
        task.handle_mission_start = calls.handle_mission_start
        task.init_for_next_round = calls.init_for_next_round
        task.skill_tick = Mock()

        def in_team():
            calls.in_team()
            return True

        task.in_team = Mock(side_effect=in_team)
        task.handle_in_mission = calls.handle_in_mission
        task.sleep = Mock(side_effect=EndIteration)
        task.stop_func = Mock()
        return task, calls

    def test_start_status_is_consumed_before_opening_actions(self):
        task, calls = self.make_task(Mission.START)

        with self.assertRaises(EndIteration):
            task.do_run()

        names = [call[0] for call in calls.mock_calls]
        self.assertLess(
            names.index("handle_mission_interface"),
            names.index("handle_in_mission"),
        )
        self.assertEqual(calls.init_all.call_count, 2)
        calls.handle_in_mission.assert_called_once()

    def test_continue_resets_round_before_opening_actions(self):
        task, calls = self.make_task(Mission.CONTINUE)

        with self.assertRaises(EndIteration):
            task.do_run()

        names = [call[0] for call in calls.mock_calls]
        self.assertLess(
            names.index("init_for_next_round"),
            names.index("handle_in_mission"),
        )
        calls.init_for_next_round.assert_called_once()
        task.skill_tick.reset.assert_called_once()
        calls.handle_in_mission.assert_called_once()


if __name__ == "__main__":
    unittest.main()
