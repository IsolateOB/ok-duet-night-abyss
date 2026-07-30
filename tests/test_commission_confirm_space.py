import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.tasks.CommissionsTask import CommissionsTask, Mission


class TestCommissionConfirmWithSpace(unittest.TestCase):

    def make_task(self):
        task = CommissionsTask.__new__(CommissionsTask)
        task.action_timeout = 15
        task.config = {}
        task.__dict__["commission_config"] = {}
        task.sleep = Mock()
        task.log_info = Mock()
        task.log_info_notify = Mock()
        task.soundBeep = Mock()
        task.choose_drop_rate_item = Mock()
        task.click_btn_random = Mock()
        task.click_box_random = Mock()
        task.click_relative_random = Mock()
        task.move_mouse_to_safe_position = Mock()
        task.move_back_from_safe_position = Mock()
        task.box_of_screen = Mock(return_value=Mock())
        task.box_of_screen_scaled = Mock(return_value=Mock())
        task.calculate_color_percentage = Mock(return_value=0.0)
        return task

    @staticmethod
    def make_wait_until():
        def _wait_until(condition, post_action=None, **kwargs):
            if post_action:
                post_action()
            return condition()

        return Mock(side_effect=_wait_until)

    def test_choose_drop_rate_confirms_with_space(self):
        task = self.make_task()
        task.__dict__["commission_config"] = {"委托手册": "100%"}
        task.find_drop_item = Mock(return_value=object())
        task.send_key = Mock()
        task.wait_until = Mock()

        task.choose_drop_rate()

        task.choose_drop_rate_item.assert_called_once()
        task.send_key.assert_called_once_with("space", down_time=0.1, after_sleep=0.25)
        task.find_drop_item.assert_not_called()
        task.wait_until.assert_not_called()
        task.click_btn_random.assert_not_called()

    def test_find_bottom_start_btn_uses_new_ui_select_letter_text(self):
        task = self.make_task()
        text_box = object()
        task.ocr = Mock(return_value=[text_box])

        result = task.find_bottom_start_btn()

        self.assertIs(result, text_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 2215, 1260, 2375, 1300, name="select_letter", hcenter=True
        )
        ocr_kwargs = task.ocr.call_args.kwargs
        self.assertIs(ocr_kwargs["box"], task.box_of_screen_scaled.return_value)
        self.assertEqual(ocr_kwargs["match"].pattern, r"选择\s*密函")

    def test_find_big_bottom_start_btn_uses_confirm_selection_text(self):
        task = self.make_task()
        confirm_box = object()
        task.ocr = Mock(return_value=[confirm_box])

        result = task.find_big_bottom_start_btn()

        self.assertIs(result, confirm_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1965, 1260, 2125, 1300, name="confirm_selection", hcenter=True
        )
        self.assertEqual(task.ocr.call_args.kwargs["match"].pattern, r"确认\s*选择")

    def test_start_mission_clicks_ocr_text_region_directly(self):
        task = self.make_task()
        start_box = object()
        task.find_retry_btn = Mock(return_value=None)
        task.find_bottom_start_btn = Mock(return_value=start_box)
        task.find_big_bottom_start_btn = Mock(return_value=None)
        task.find_drop_rate_btn = Mock(return_value=None)
        task.find_letter_interface = Mock(return_value=object())
        task.wait_until = Mock(return_value=True)

        task.start_mission()

        task.click_box_random.assert_called_once_with(
            start_box, down_time=0.02, after_sleep=0.2
        )
        task.click_btn_random.assert_not_called()

    def test_find_ingame_continue_uses_new_ui_again_text(self):
        task = self.make_task()
        continue_box = object()
        task.ocr = Mock(return_value=[continue_box])

        result = task.find_ingame_continue_btn()

        self.assertIs(result, continue_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1760, 1250, 1930, 1295, name="continue_mission", hcenter=True
        )
        self.assertEqual(task.ocr.call_args.kwargs["match"].pattern, r"再次\s*进行")

    def test_find_continue_challenge_uses_endless_mode_text(self):
        task = self.make_task()
        continue_box = object()
        task.ocr = Mock(return_value=[continue_box])

        result = task.find_continue_challenge_btn()

        self.assertIs(result, continue_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1660, 970, 1800, 1010, name="continue_challenge", hcenter=True
        )
        self.assertEqual(task.ocr.call_args.kwargs["match"].pattern, r"继续\s*挑战")

    def test_continue_mission_clicks_ocr_again_region(self):
        task = self.make_task()
        task.in_team = Mock(return_value=False)
        state = {"open": True}
        continue_box = object()
        task.find_ingame_continue_btn = Mock(
            side_effect=lambda: continue_box if state["open"] else None
        )

        def click_box(*args, **kwargs):
            state["open"] = False

        task.click_box_random = Mock(side_effect=click_box)
        task.wait_until = self.make_wait_until()
        task.pending_drop_rate_choice = False

        result = task.continue_mission()

        self.assertTrue(result)
        self.assertTrue(task.pending_drop_rate_choice)
        task.click_box_random.assert_called_once_with(
            continue_box,
            down_time=0.1,
            after_sleep=0.5,
            force_background=True,
        )
        self.assertEqual(task.wait_until.call_count, 2)

    def test_continue_mission_ocr_recheck_loss_returns_false(self):
        task = self.make_task()
        task.in_team = Mock(return_value=False)
        task.wait_until = Mock(return_value=False)
        task.pending_drop_rate_choice = False

        result = task.continue_mission()

        self.assertFalse(result)
        self.assertFalse(task.pending_drop_rate_choice)
        task.click_box_random.assert_not_called()

    def test_failed_continue_does_not_set_continue_status(self):
        task = self.make_task()
        task.mission_status = None
        task.pending_drop_rate_choice = False
        task.in_team = Mock(return_value=False)
        task.check_for_monthly_card = Mock()
        task.find_letter_reward_btn = Mock(return_value=None)
        task.find_letter_interface = Mock(return_value=None)
        task.find_drop_rate_btn = Mock(return_value=None)
        task.find_continue_challenge_btn = Mock(return_value=None)
        task.find_retry_btn = Mock(return_value=None)
        task.find_bottom_start_btn = Mock(return_value=None)
        task.find_big_bottom_start_btn = Mock(return_value=None)
        task.find_ingame_continue_btn = Mock(return_value=object())
        task.continue_mission = Mock(return_value=False)

        result = task.handle_mission_interface()

        self.assertIsNone(result)
        self.assertIsNone(task.mission_status)

    def test_continue_challenge_clicks_ocr_text_region(self):
        task = self.make_task()
        task.in_team = Mock(return_value=False)
        state = {"open": True}
        continue_box = object()
        task.find_continue_challenge_btn = Mock(
            side_effect=lambda: continue_box if state["open"] else None
        )

        def click_box(*args, **kwargs):
            state["open"] = False

        task.click_box_random = Mock(side_effect=click_box)
        task.wait_until = self.make_wait_until()

        result = task.continue_challenge()

        self.assertTrue(result)
        task.click_box_random.assert_called_once_with(
            continue_box, down_time=0.02, after_sleep=0.5
        )
        self.assertEqual(task.wait_until.call_count, 2)

    def test_find_letter_reward_uses_confirm_selection_text(self):
        task = self.make_task()
        confirm_box = object()
        task.ocr = Mock(return_value=[confirm_box])

        result = task.find_letter_reward_btn()

        self.assertIs(result, confirm_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1195, 1170, 1360, 1215, name="letter_reward_confirm", hcenter=True
        )
        self.assertEqual(
            task.ocr.call_args.kwargs["match"].pattern,
            r"确认\s*选择",
        )

    def test_find_give_up_confirm_uses_updated_ocr_region(self):
        task = self.make_task()
        confirm_box = object()
        task.ocr = Mock(return_value=[confirm_box])

        result = task.find_give_up_confirm_btn()

        self.assertIs(result, confirm_box)
        task.box_of_screen_scaled.assert_called_once_with(
            2560, 1440, 1495, 815, 1580, 855, name="give_up_confirm", hcenter=True
        )
        self.assertEqual(task.ocr.call_args.kwargs["match"].pattern, r"确\s*定")

    def test_give_up_mission_clicks_ocr_confirm_text(self):
        task = self.make_task()
        confirm_box = object()
        state = {"confirm_open": False}
        task.open_in_mission_menu = Mock(return_value=True)
        task.find_give_up_confirm_btn = Mock(
            side_effect=lambda: confirm_box if state["confirm_open"] else None
        )
        task.find_retry_btn = Mock(return_value=object())
        task.find_bottom_start_btn = Mock(return_value=None)
        task.find_big_bottom_start_btn = Mock(return_value=None)
        task.find_ingame_continue_btn = Mock(return_value=None)
        task.find_esc_menu = Mock(return_value=None)

        def click_exit(*args, **kwargs):
            state["confirm_open"] = True

        def click_confirm(*args, **kwargs):
            state["confirm_open"] = False

        task.click_relative_random = Mock(side_effect=click_exit)
        task.click_box_random = Mock(side_effect=click_confirm)
        task.wait_until = self.make_wait_until()

        result = task.give_up_mission()

        self.assertTrue(result)
        task.click_relative_random.assert_called_once_with(
            0.885, 0.875, 0.965, 0.954, after_sleep=0.25
        )
        task.click_box_random.assert_called_once_with(
            confirm_box, down_time=0.1, after_sleep=0.5
        )

    def test_choose_drop_rate_item_uses_2k_scaled_blind_click_regions(self):
        task = self.make_task()
        task.choose_drop_rate_item = CommissionsTask.choose_drop_rate_item.__get__(task, CommissionsTask)
        task.mission_status = None
        task.current_round = 0
        cases = {
            "100%": (1000 / 2560, 775 / 1440, 1145 / 2560, 820 / 1440),
            "200%": (1200 / 2560, 775 / 1440, 1360 / 2560, 820 / 1440),
            "800%": (1410 / 2560, 775 / 1440, 1565 / 2560, 820 / 1440),
            "2000%": (1615 / 2560, 775 / 1440, 1775 / 2560, 820 / 1440),
        }

        for drop_rate, expected_region in cases.items():
            with self.subTest(drop_rate=drop_rate):
                task.click_relative_random.reset_mock()
                task.__dict__["commission_config"] = {"委托手册": drop_rate}

                task.choose_drop_rate_item()

                task.click_relative_random.assert_called_once_with(*expected_region)

    def test_reset_and_transport_uses_updated_important_position_reset_y_region(self):
        task = self.make_task()
        task.open_in_mission_menu = Mock()
        task.find_esc_menu = Mock(return_value=None)
        task.find_one = Mock(return_value=Mock())
        task.click_box_random = Mock()
        task.find_start_btn = Mock(return_value=Mock())
        task.in_team = Mock(return_value=True)
        task.ensure_main = Mock()

        def wait_until(condition, post_action=None, **kwargs):
            if post_action:
                post_action()
            return condition()

        task.wait_until = Mock(side_effect=wait_until)

        task.reset_and_transport()

        task.click_relative_random.assert_any_call(
            0.5078,
            850 / 1440,
            0.6836,
            895 / 1440,
            after_sleep=0.5,
            use_safe_move=True,
            safe_move_box=task.box_of_screen_scaled.return_value,
        )

    def test_choose_letter_confirms_with_space_without_button_image(self):
        task = self.make_task()
        task.__dict__["commission_config"] = {"自动处理密函": True}
        state = {"dialog_open": True}

        task.find_letter_btn = Mock(return_value=None)
        task.find_not_use_letter_icon = Mock(return_value=Mock())

        def find_letter_interface():
            return object() if state["dialog_open"] else None

        def send_key(*args, **kwargs):
            state["dialog_open"] = False

        task.find_letter_interface = Mock(side_effect=find_letter_interface)
        task.send_key = Mock(side_effect=send_key)
        task.wait_until = self.make_wait_until()

        task.choose_letter()

        task.send_key.assert_called_once_with("space", down_time=0.1, after_sleep=1)
        task.click_btn_random.assert_not_called()

    def test_letter_selection_preserves_start_status_for_reward_detection(self):
        task = self.make_task()
        task.mission_status = Mission.START
        task.in_team = Mock(return_value=False)
        task.check_for_monthly_card = Mock()
        task.find_letter_reward_btn = Mock(return_value=None)
        task.find_letter_interface = Mock(return_value=object())
        task.choose_letter = Mock()

        result = task.handle_mission_interface()

        self.assertIsNone(result)
        self.assertIs(task.mission_status, Mission.START)
        task.choose_letter.assert_called_once()

    def test_letter_reward_preserves_start_status_until_team_is_entered(self):
        task = self.make_task()
        task.mission_status = Mission.START
        task.in_team = Mock(return_value=False)
        task.check_for_monthly_card = Mock()
        task.find_letter_reward_btn = Mock(return_value=object())
        task.choose_letter_reward = Mock()

        result = task.handle_mission_interface()

        self.assertIsNone(result)
        self.assertIs(task.mission_status, Mission.START)
        task.choose_letter_reward.assert_called_once()

    def test_entering_team_consumes_preserved_start_status(self):
        task = self.make_task()
        task.mission_status = Mission.START
        task.pending_drop_rate_choice = True
        task.in_team = Mock(return_value=True)

        result = task.handle_mission_interface()

        self.assertIs(result, Mission.START)
        self.assertIsNone(task.mission_status)
        self.assertFalse(task.pending_drop_rate_choice)

    def test_continue_challenge_preserves_continue_status_until_team_is_entered(self):
        task = self.make_task()
        task.mission_status = None
        task.pending_drop_rate_choice = False
        task.in_team = Mock(return_value=False)
        task.check_for_monthly_card = Mock()
        task.find_letter_reward_btn = Mock(return_value=None)
        task.find_letter_interface = Mock(return_value=None)
        task.find_drop_rate_btn = Mock(return_value=None)
        task.find_continue_challenge_btn = Mock(return_value=object())
        task.continue_challenge = Mock(return_value=True)

        result = task.handle_mission_interface()

        self.assertIsNone(result)
        self.assertIs(task.mission_status, Mission.CONTINUE)
        task.continue_challenge.assert_called_once()

    def test_pending_drop_rate_rechecks_reward_before_blind_choice(self):
        task = self.make_task()
        task.mission_status = Mission.CONTINUE
        task.pending_drop_rate_choice = True
        task.in_team = Mock(side_effect=[False, False])
        task.check_for_monthly_card = Mock()
        task.find_letter_reward_btn = Mock(side_effect=[None, object()])
        task.find_letter_interface = Mock(return_value=None)
        task.find_drop_rate_btn = Mock(return_value=None)
        task.choose_drop_rate = Mock()

        result = task.handle_mission_interface()

        self.assertIsNone(result)
        self.assertFalse(task.pending_drop_rate_choice)
        self.assertIs(task.mission_status, Mission.CONTINUE)
        task.choose_drop_rate.assert_not_called()

    def test_drop_rate_selection_preserves_status_until_team_is_entered(self):
        task = self.make_task()
        task.mission_status = Mission.CONTINUE
        task.pending_drop_rate_choice = True
        task.in_team = Mock(return_value=False)
        task.check_for_monthly_card = Mock()
        task.find_letter_reward_btn = Mock(return_value=None)
        task.find_letter_interface = Mock(return_value=None)
        task.find_drop_rate_btn = Mock(return_value=object())
        task.choose_drop_rate = Mock()

        result = task.handle_mission_interface()

        self.assertIsNone(result)
        self.assertFalse(task.pending_drop_rate_choice)
        self.assertIs(task.mission_status, Mission.CONTINUE)
        task.choose_drop_rate.assert_called_once()

    def test_letter_reward_confirm_timeout_returns_for_retry(self):
        task = self.make_task()
        task.__dict__["commission_config"] = {
            "自动处理密函": True,
            "密函奖励偏好": "不使用",
        }
        task.wait_until = Mock(return_value=False)

        result = task.choose_letter_reward()

        self.assertFalse(result)
        task.log_info_notify.assert_called_once_with("密函奖励确认超时，将在下一轮重试")

    def test_letter_reward_clicks_ocr_confirm_region(self):
        task = self.make_task()
        task.__dict__["commission_config"] = {
            "自动处理密函": True,
            "密函奖励偏好": "不使用",
        }
        state = {"open": True}
        confirm_box = object()
        task.find_letter_reward_btn = Mock(
            side_effect=lambda: confirm_box if state["open"] else None
        )

        def click_box(*args, **kwargs):
            state["open"] = False

        task.click_box_random = Mock(side_effect=click_box)
        task.wait_until = self.make_wait_until()
        task.in_team = Mock(return_value=False)

        result = task.choose_letter_reward()

        self.assertTrue(result)
        task.click_box_random.assert_called_once_with(
            confirm_box, down_time=0.1, after_sleep=0.5
        )

    def test_letter_reward_ocr_uses_updated_region(self):
        task = self.make_task()
        task.__dict__["commission_config"] = {"密函奖励偏好": "持有数最少"}
        task.click_box_random = Mock()
        rewards = [
            SimpleNamespace(x=100, name="持有数: 5"),
            SimpleNamespace(x=200, name="持有数: 2"),
            SimpleNamespace(x=300, name="持有数: 8"),
        ]
        task.ocr = Mock(return_value=rewards)

        task.choose_target_letter_reward()

        task.box_of_screen.assert_called_with(
            0.320,
            0.640,
            0.675,
            0.678,
            hcenter=True,
            name="letter_reward",
        )
        task.click_box_random.assert_called_once()


if __name__ == "__main__":
    unittest.main()
