"""Tests for Calculator application."""

import unittest
import unittest.mock as mock
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCalculatorLogic(unittest.TestCase):
    """Test Calculator logic functions with mocked GUI."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Mock the tkinter module before importing calc
        self.mock_tkinter = mock.MagicMock()
        self.mock_tkinter.Tk.return_value = mock.MagicMock()
        self.mock_tkinter.Toplevel.return_value = mock.MagicMock()
        self.mock_tkinter.StringVar.return_value = mock.MagicMock()
        self.mock_tkinter.IntVar.return_value = mock.MagicMock()
        self.mock_tkinter.TclError = Exception
        
        # Patch tkinter globally
        self.tkinter_patcher = mock.patch.dict('sys.modules', {'tkinter': self.mock_tkinter})
        self.tkinter_patcher.start()
        
        # Need to reload calc module to use mocked tkinter
        if 'calc' in sys.modules:
            del sys.modules['calc']
        
        import calc
        self.calc = calc
        
        # Override file paths to use temp directory
        calc.HISTORY_FILE = os.path.join(self.test_dir, "history.json")
        calc.SETTINGS_FILE = os.path.join(self.test_dir, "settings.json")
        
    def tearDown(self):
        """Clean up after tests."""
        self.tkinter_patcher.stop()
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_load_settings_with_no_file(self):
        """Test loading settings when file doesn't exist."""
        # Create Calculator instance with mocked GUI
        with mock.patch.object(self.calc.Calculator, 'load_history', return_value=[]):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        result = calc_obj.load_settings()
        
        self.assertIn('history_retention_days', result)
        self.assertEqual(result['history_retention_days'], 30)

    def test_load_settings_with_existing_file(self):
        """Test loading settings from existing file."""
        # Create settings file
        test_settings = {'history_retention_days': 15, 'custom_key': 'value'}
        with open(self.calc.SETTINGS_FILE, 'w') as f:
            json.dump(test_settings, f)
        
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_history', return_value=[]):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        result = calc_obj.load_settings()
        
        self.assertEqual(result['history_retention_days'], 15)
        self.assertEqual(result['custom_key'], 'value')

    def test_save_settings(self):
        """Test saving settings to file."""
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_history', return_value=[]):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
                calc_obj.settings = {'history_retention_days': 45}
        
        calc_obj.save_settings()
        
        # Verify file was created with correct content
        self.assertTrue(os.path.exists(self.calc.SETTINGS_FILE))
        with open(self.calc.SETTINGS_FILE, 'r') as f:
            saved_settings = json.load(f)
        self.assertEqual(saved_settings['history_retention_days'], 45)

    def test_load_history_with_no_file(self):
        """Test loading history when file doesn't exist."""
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        result = calc_obj.load_history()
        
        self.assertEqual(result, [])

    def test_load_history_with_existing_file(self):
        """Test loading history from existing file."""
        # Create history file
        test_history = [
            {'expression': '2+2', 'result': '4', 'timestamp': '2024-01-01T12:00:00'},
            {'expression': '5*3', 'result': '15', 'timestamp': '2024-01-01T12:01:00'}
        ]
        with open(self.calc.HISTORY_FILE, 'w') as f:
            json.dump(test_history, f)
        
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        result = calc_obj.load_history()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['expression'], '2+2')
        self.assertEqual(result[1]['result'], '15')

    def test_save_history(self):
        """Test saving history to file."""
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
                calc_obj.history = [
                    {'expression': '2+2', 'result': '4', 'timestamp': '2024-01-01T12:00:00'}
                ]
        
        calc_obj.save_history()
        
        # Verify file was created with correct content
        self.assertTrue(os.path.exists(self.calc.HISTORY_FILE))
        with open(self.calc.HISTORY_FILE, 'r') as f:
            saved_history = json.load(f)
        self.assertEqual(len(saved_history), 1)
        self.assertEqual(saved_history[0]['expression'], '2+2')

    def test_add_to_history(self):
        """Test adding entry to history."""
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        calc_obj.add_to_history('5+5', '10')
        
        self.assertEqual(len(calc_obj.history), 1)
        self.assertEqual(calc_obj.history[0]['expression'], '5+5')
        self.assertEqual(calc_obj.history[0]['result'], '10')
        self.assertIn('timestamp', calc_obj.history[0])

    def test_purge_old_history(self):
        """Test purging old history entries."""
        # Create Calculator instance with old history
        old_timestamp = (datetime.now() - timedelta(days=40)).isoformat()
        new_timestamp = (datetime.now() - timedelta(days=5)).isoformat()
        
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            calc_obj = self.calc.Calculator()
            calc_obj.history = [
                {'expression': 'old', 'result': '1', 'timestamp': old_timestamp},
                {'expression': 'new', 'result': '2', 'timestamp': new_timestamp}
            ]
            calc_obj.settings = {'history_retention_days': 30}
        
        calc_obj.purge_old_history()
        
        # Old entry should be removed, new should remain
        self.assertEqual(len(calc_obj.history), 1)
        self.assertEqual(calc_obj.history[0]['expression'], 'new')


class TestSettingsScreen(unittest.TestCase):
    """Test SettingsScreen class with mocked tkinter."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the tkinter module
        self.mock_tkinter = mock.MagicMock()
        self.mock_tkinter.Toplevel.return_value = mock.MagicMock()
        
        # Patch tkinter globally
        self.tkinter_patcher = mock.patch.dict('sys.modules', {'tkinter': self.mock_tkinter})
        self.tkinter_patcher.start()
        
        # Need to reload calc module to use mocked tkinter
        if 'calc' in sys.modules:
            del sys.modules['calc']
        
        import calc
        self.calc = calc
        
    def tearDown(self):
        """Clean up after tests."""
        self.tkinter_patcher.stop()

    def test_settings_screen_init(self):
        """Test SettingsScreen initialization."""
        settings = {'theme': 'Dark', 'decimal_precision': 5}
        on_save_callback = mock.MagicMock()
        
        screen = self.calc.SettingsScreen(None, settings, on_save_callback)
        
        self.assertEqual(screen.settings['theme'], 'Dark')
        self.assertEqual(screen.settings['decimal_precision'], 5)
        self.assertEqual(screen.on_save, on_save_callback)

    def test_settings_screen_on_option_change(self):
        """Test option change handler."""
        settings = {'theme': 'Light'}
        on_save_callback = mock.MagicMock()
        
        screen = self.calc.SettingsScreen(None, settings, on_save_callback)
        
        # Create mock var
        mock_var = mock.MagicMock()
        mock_var.get.return_value = 'Dark'
        
        screen._on_option_change('theme', mock_var)
        
        self.assertEqual(screen.settings['theme'], 'Dark')

    def test_settings_screen_on_spinbox_change(self):
        """Test spinbox change handler."""
        settings = {'decimal_precision': 10}
        on_save_callback = mock.MagicMock()
        
        screen = self.calc.SettingsScreen(None, settings, on_save_callback)
        
        # Create mock var
        mock_var = mock.MagicMock()
        mock_var.get.return_value = 8
        
        screen._on_spinbox_change('decimal_precision', mock_var)
        
        self.assertEqual(screen.settings['decimal_precision'], 8)

    def test_settings_screen_history_retention_in_settings(self):
        """Test that history retention is included in settings."""
        settings = {'theme': 'Light', 'history_retention_days': 30}
        on_save_callback = mock.MagicMock()
        
        screen = self.calc.SettingsScreen(None, settings, on_save_callback)
        
        # Verify history_retention_days is in settings
        self.assertIn('history_retention_days', screen.settings)


class TestTheme(unittest.TestCase):
    """Test theme functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the tkinter module
        self.mock_tkinter = mock.MagicMock()
        self.mock_tkinter.Tk.return_value = mock.MagicMock()
        self.mock_tkinter.Toplevel.return_value = mock.MagicMock()
        self.mock_tkinter.StringVar.return_value = mock.MagicMock()
        self.mock_tkinter.IntVar.return_value = mock.MagicMock()
        self.mock_tkinter.TclError = Exception
        
        # Patch tkinter globally
        self.tkinter_patcher = mock.patch.dict('sys.modules', {'tkinter': self.mock_tkinter})
        self.tkinter_patcher.start()
        
        # Need to reload calc module to use mocked tkinter
        if 'calc' in sys.modules:
            del sys.modules['calc']
        
        import calc
        self.calc = calc
        
    def tearDown(self):
        """Clean up after tests."""
        self.tkinter_patcher.stop()

    def test_apply_theme_light(self):
        """Test applying light theme."""
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        # Call apply_theme
        calc_obj.apply_theme("Light")
        
        # Verify widget configurations were called
        calc_obj.window.configure.assert_called()
        calc_obj.display_frame.configure.assert_called()
        calc_obj.total_label.configure.assert_called()
        calc_obj.label.configure.assert_called()

    def test_apply_theme_dark(self):
        """Test applying dark theme."""
        # Create Calculator instance
        with mock.patch.object(self.calc.Calculator, 'load_settings', return_value={'history_retention_days': 30}):
            with mock.patch.object(self.calc.Calculator, 'purge_old_history'):
                calc_obj = self.calc.Calculator()
        
        # Call apply_theme
        calc_obj.apply_theme("Dark")
        
        # Verify widget configurations were called
        calc_obj.window.configure.assert_called()
        calc_obj.display_frame.configure.assert_called()
        calc_obj.total_label.configure.assert_called()
        calc_obj.label.configure.assert_called()


if __name__ == '__main__':
    unittest.main()
