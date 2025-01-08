import unittest
from unittest.mock import patch, MagicMock
import os
import json
from main import get_pixabay_api_key, select_input_file, get_deck_name, validate_input_file, load_config

class TestMainFunctions(unittest.TestCase):

    @patch('builtins.input', return_value='valid_api_key')
    @patch('main.save_config')
    def pixabay_api_key_saved_to_config(self, mock_save_config, mock_input):
        config = {}
        api_key = get_pixabay_api_key(config)
        self.assertEqual(api_key, 'valid_api_key')
        mock_save_config.assert_called_once()

    @patch('builtins.input', return_value='')
    def pixabay_api_key_missing_exits(self, mock_input):
        config = {}
        with self.assertRaises(SystemExit):
            get_pixabay_api_key(config)

    @patch('main.get_default_input_files', return_value=['file1.md', 'file2.md'])
    @patch('builtins.input', return_value='1')
    def select_input_file_from_list(self, mock_input, mock_get_default_input_files):
        selected_file = select_input_file()
        self.assertEqual(selected_file, os.path.join('input_files', 'file1.md'))

    @patch('main.filedialog.askopenfilename', return_value='selected_file.md')
    def select_input_file_manually(self, mock_askopenfilename):
        selected_file = select_input_file()
        self.assertEqual(selected_file, 'selected_file.md')

    @patch('builtins.input', return_value='')
    def deck_name_missing_exits(self, mock_input):
        with self.assertRaises(SystemExit):
            get_deck_name()

    @patch('builtins.input', return_value='valid_deck_name')
    def deck_name_valid(self, mock_input):
        deck_name = get_deck_name()
        self.assertEqual(deck_name, 'valid_deck_name')

    def validate_input_file_valid(self):
        self.assertTrue(validate_input_file('valid_file.md'))

    def validate_input_file_invalid(self):
        self.assertFalse(validate_input_file('invalid_file.txt'))

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"pixabay_api_key": "key"}')
    def load_config_valid(self, mock_open):
        config = load_config('config.json')
        self.assertEqual(config, {"pixabay_api_key": "key"})

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='invalid_json')
    def load_config_invalid(self, mock_open):
        config = load_config('config.json')
        self.assertIsNone(config)

if __name__ == '__main__':
    unittest.main()