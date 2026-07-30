import unittest
from unittest.mock import ANY, Mock

from src.tasks.BaseDNATask import BaseDNATask


class TestBaseDNATaskClick(unittest.TestCase):

    def test_foreground_click_uses_fixed_coordinates(self):
        class ClickTask(BaseDNATask):
            @property
            def hwnd(self):
                return self.test_hwnd

            @property
            def pydirect_interaction(self):
                return self.test_interaction

            def sleep(self, seconds):
                self.test_sleep(seconds)

        task = ClickTask.__new__(ClickTask)
        task.test_hwnd = Mock()
        task.test_hwnd.is_foreground.return_value = True
        task.test_interaction = Mock()
        task.test_sleep = Mock()

        task._perform_random_click(123, 456, down_time=0.02)

        task.test_interaction.move.assert_not_called()
        task.test_interaction.click.assert_called_once_with(
            123, 456, down_time=ANY
        )

    def test_background_click_always_releases_mouse(self):
        class ClickTask(BaseDNATask):
            @property
            def hwnd(self):
                return self.test_hwnd

            @property
            def executor(self):
                return self.test_executor

            def sleep(self, seconds):
                if self.raise_while_pressed and self.test_interaction.mouse_down.called:
                    raise RuntimeError("interrupted")
                self.test_sleep(seconds)

        task = ClickTask.__new__(ClickTask)
        task.test_hwnd = Mock()
        task.test_hwnd.is_foreground.return_value = False
        task.test_interaction = Mock()
        task.test_executor = Mock(interaction=task.test_interaction)
        task.test_sleep = Mock()
        task.raise_while_pressed = True

        with self.assertRaisesRegex(RuntimeError, "interrupted"):
            task._perform_random_click(123, 456, down_time=0.02)

        task.test_interaction.move.assert_called_once_with(123, 456)
        task.test_interaction.mouse_down.assert_called_once_with(123, 456)
        task.test_interaction.mouse_up.assert_called_once_with()

    def test_force_background_does_not_move_real_mouse_when_game_is_foreground(self):
        class ClickTask(BaseDNATask):
            @property
            def hwnd(self):
                return self.test_hwnd

            @property
            def executor(self):
                return self.test_executor

            @property
            def pydirect_interaction(self):
                return self.test_real_interaction

            def sleep(self, seconds):
                self.test_sleep(seconds)

        task = ClickTask.__new__(ClickTask)
        task.test_hwnd = Mock()
        task.test_hwnd.is_foreground.return_value = True
        task.test_background_interaction = Mock()
        task.test_executor = Mock(interaction=task.test_background_interaction)
        task.test_real_interaction = Mock()
        task.test_sleep = Mock()

        task._perform_random_click(
            123, 456, down_time=0.1, force_background=True
        )

        task.test_real_interaction.click.assert_not_called()
        task.test_background_interaction.move.assert_called_once_with(123, 456)
        task.test_background_interaction.mouse_down.assert_called_once_with(123, 456)
        task.test_background_interaction.mouse_up.assert_called_once_with()

if __name__ == "__main__":
    unittest.main()
