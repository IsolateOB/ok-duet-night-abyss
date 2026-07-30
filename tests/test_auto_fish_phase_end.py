import unittest
from unittest.mock import Mock, patch

from src.tasks.fullauto.AutoFishTask import AutoFishTask


class TestAutoFishPhaseEnd(unittest.TestCase):

    def make_task(self, *, cast_sequence, chance_sequence=None, bite_sequence=None):
        task = AutoFishTask.__new__(AutoFishTask)
        task.config = {
            "END_WAIT_SPACE": 0.0,
            "MAX_END_SEC": 10.0,
        }
        task.stats = {}
        task.info_set = Mock()
        task.send_key = Mock()
        task.next_frame = Mock()
        task.click_relative_random = Mock()

        task.find_fish_cast = Mock(side_effect=self.sequence_finder(cast_sequence))
        task.find_fish_chance = Mock(side_effect=self.sequence_finder(chance_sequence or [False]))
        task.find_fish_bite = Mock(side_effect=self.sequence_finder(bite_sequence or [False]))
        return task

    @staticmethod
    def sequence_finder(sequence):
        values = iter(sequence)

        def find_icon():
            try:
                return next(values), (0, 0)
            except StopIteration:
                return sequence[-1], (0, 0)

        return find_icon

    def run_phase_end_with_fake_clock(self, task):
        now = {"value": 0.0}

        def sleep(seconds):
            now["value"] += seconds

        task.sleep = Mock(side_effect=sleep)

        with patch("src.tasks.fullauto.AutoFishTask.time.monotonic", side_effect=lambda: now["value"]):
            result = AutoFishTask.phase_end(task)

        return result, now["value"]

    def test_phase_end_waits_for_icons_to_disappear_before_clicking_settlement(self):
        task = self.make_task(cast_sequence=[True, True, True, False, False, False, False, True, True])

        result, elapsed = self.run_phase_end_with_fake_clock(task)

        self.assertTrue(result)
        self.assertGreaterEqual(elapsed, 2.5)
        task.send_key.assert_not_called()
        task.click_relative_random.assert_any_call(0.05, 0.3, 0.4, 0.7)
        self.assertGreaterEqual(task.next_frame.call_count, 8)

    def test_phase_end_keeps_clicking_settlement_until_cast_returns(self):
        task = self.make_task(cast_sequence=[False, False, False, False, False, True, True])

        result, _ = self.run_phase_end_with_fake_clock(task)

        self.assertTrue(result)
        task.send_key.assert_not_called()
        self.assertGreaterEqual(task.click_relative_random.call_count, 2)
        task.click_relative_random.assert_any_call(0.05, 0.3, 0.4, 0.7)

    def test_phase_end_accepts_chance_icon_after_settlement(self):
        task = self.make_task(
            cast_sequence=[False, False, False, False, False, False],
            chance_sequence=[False, False, False, True, True],
        )

        result, _ = self.run_phase_end_with_fake_clock(task)

        self.assertTrue(result)
        task.send_key.assert_not_called()
        task.click_relative_random.assert_any_call(0.05, 0.3, 0.4, 0.7)

    def test_phase_end_rejects_when_icons_never_disappear(self):
        task = self.make_task(cast_sequence=[True])

        result, elapsed = self.run_phase_end_with_fake_clock(task)

        self.assertFalse(result)
        self.assertGreaterEqual(elapsed, 10.0)
        task.send_key.assert_not_called()

    def test_do_run_retries_phase_end_without_starting_next_round(self):
        task = AutoFishTask.__new__(AutoFishTask)
        task.config = {"MAX_ROUNDS": 1}
        task.stats = {}
        task.info_set = Mock()
        task.soundBeep = Mock()
        task.sleep = Mock()
        task.find_fish_chance = Mock(return_value=(False, (0, 0)))
        task.phase_start = Mock(return_value=True)
        task.phase_fight = Mock(return_value=True)
        task.phase_end = Mock(side_effect=[False, True])

        AutoFishTask.do_run(task)

        task.phase_start.assert_called_once()
        task.phase_fight.assert_called_once()
        self.assertEqual(task.phase_end.call_count, 2)


if __name__ == "__main__":
    unittest.main()
