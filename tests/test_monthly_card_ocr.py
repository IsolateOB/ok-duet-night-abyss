import time
import unittest
from unittest.mock import Mock

from src.tasks.BaseDNATask import BaseDNATask


class TestMonthlyCardOcr(unittest.TestCase):

    def make_task(self):
        task = BaseDNATask.__new__(BaseDNATask)
        task.box_of_screen_scaled = Mock(return_value=Mock())
        return task

    def test_close_hint_uses_updated_ocr_region(self):
        task = self.make_task()
        text_box = object()
        task.ocr = Mock(return_value=[text_box])

        result = task.find_monthly_card_close_hint()

        self.assertIs(result, text_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1180, 1260, 1375, 1290,
            name="monthly_card_close_hint", hcenter=True
        )
        self.assertEqual(
            task.ocr.call_args.kwargs["match"].pattern,
            r"点击\s*空白\s*区域\s*关闭",
        )

    def test_attendance_uses_updated_ocr_region(self):
        task = self.make_task()
        text_box = object()
        task.ocr = Mock(return_value=[text_box])

        result = task.find_monthly_card_attendance()

        self.assertIs(result, text_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1555, 315, 2020, 380,
            name="monthly_card_attendance", hcenter=True
        )
        self.assertEqual(
            task.ocr.call_args.kwargs["match"].pattern,
            r"水仙\s*平原\s*出勤\s*积累",
        )

    def test_handler_clicks_fixed_point_until_both_texts_disappear(self):
        task = self.make_task()
        state = {"screen": 2}
        close_hint = object()
        attendance = object()
        task.find_monthly_card_close_hint = Mock(
            side_effect=lambda: close_hint if state["screen"] == 2 else None
        )
        task.find_monthly_card_attendance = Mock(
            side_effect=lambda: attendance if state["screen"] == 1 else None
        )
        task._last_monthly_card_check_time = time.time()
        task.screenshot = Mock()
        task.width_of_screen = Mock(return_value=2090)
        task.height_of_screen = Mock(return_value=370)
        task._perform_random_click = Mock(
            side_effect=lambda *args, **kwargs: state.update(
                screen=state["screen"] - 1
            )
        )
        task.set_check_monthly_card = Mock()

        def wait_until(condition, post_action=None, **kwargs):
            for _ in range(3):
                if condition():
                    return True
                post_action()
            return condition()

        task.wait_until = Mock(side_effect=wait_until)

        result = task.handle_monthly_card()

        self.assertTrue(result)
        self.assertEqual(task._perform_random_click.call_count, 2)
        task._perform_random_click.assert_called_with(
            2090,
            370,
            down_time=0.1,
            after_sleep=0.5,
            force_background=True,
        )
        task.set_check_monthly_card.assert_called_once_with(next_day=True)


if __name__ == "__main__":
    unittest.main()
