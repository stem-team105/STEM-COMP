"""Launcher recovery checks. No packages or model downloads run during tests."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import launcher


class LauncherTests(unittest.TestCase):
    def test_existing_install_opens_without_network_setup(self):
        with tempfile.TemporaryDirectory(prefix='Lamatna family ') as folder:
            root = Path(folder)
            python = launcher.environment_python(root)
            python.parent.mkdir(parents=True)
            python.touch()
            run = Mock()
            with patch.object(launcher, 'has_interface', return_value=True):
                self.assertEqual(launcher.prepare_environment(root, run, Mock()), python)
            run.assert_not_called()

    def test_fresh_setup_is_isolated_and_handles_spaces(self):
        with tempfile.TemporaryDirectory(prefix='Lamatna family ') as folder:
            root = Path(folder)
            run = Mock()
            with patch.object(launcher, 'has_interface', side_effect=[False, True]):
                python = launcher.prepare_environment(root, run, Mock())
            calls = [call.args[0] for call in run.call_args_list]
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][-1], str(root / '.venv'))
            self.assertEqual(calls[1][0], str(python))
            self.assertIn(str(root / 'requirements.txt'), calls[1])
            self.assertFalse((root / 'models').exists())

    def test_failed_interface_repair_stops_with_useful_error(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            python = launcher.environment_python(root)
            python.parent.mkdir(parents=True)
            python.touch()
            with patch.object(launcher, 'has_interface', return_value=False):
                with self.assertRaisesRegex(RuntimeError, 'startup.log'):
                    launcher.prepare_environment(root, Mock(), Mock())

    def test_support_download_failure_does_not_report_completion(self):
        run = Mock(side_effect=RuntimeError('No connection'))
        with self.assertRaisesRegex(RuntimeError, 'No connection'):
            launcher.install_game_support(Path('family app'), Path('python.exe'), run, Mock())
        self.assertEqual(run.call_count, 1)


if __name__ == '__main__':
    unittest.main()
