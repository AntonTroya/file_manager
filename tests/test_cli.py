import unittest
from unittest.mock import patch, MagicMock
import sys
from cli import main


class TestCLI(unittest.TestCase):
    
    @patch('sys.argv', ['cli.py', 'copy', 'source.txt', 'dest.txt'])
    @patch('cli.copy_file')
    def test_copy_command(self, mock_copy):
        mock_copy.return_value = True
        with patch('builtins.print') as mock_print:
            main()
            mock_copy.assert_called_once_with('source.txt', 'dest.txt')
    
    @patch('sys.argv', ['cli.py', 'delete', 'test.txt'])
    @patch('cli.delete_path')
    def test_delete_command(self, mock_delete):
        mock_delete.return_value = True
        with patch('builtins.print') as mock_print:
            main()
            mock_delete.assert_called_once_with('test.txt', False)
    
    @patch('sys.argv', ['cli.py', 'delete', 'test_dir', '--recursive'])
    @patch('cli.delete_path')
    def test_delete_command_recursive(self, mock_delete):
        mock_delete.return_value = True
        with patch('builtins.print') as mock_print:
            main()
            mock_delete.assert_called_once_with('test_dir', True)
    
    @patch('sys.argv', ['cli.py', 'count', 'folder'])
    @patch('cli.count_files_in_folder')
    def test_count_command(self, mock_count):
        mock_count.return_value = 10
        with patch('builtins.print') as mock_print:
            main()
            mock_count.assert_called_once_with('folder')
            mock_print.assert_called_with("Количество файлов в папке folder: 10")
    
    @patch('sys.argv', ['cli.py', 'search', 'folder', '.*\\.txt$'])
    @patch('cli.find_files_by_pattern')
    def test_search_command(self, mock_search):
        mock_search.return_value = ['file1.txt', 'file2.txt']
        with patch('builtins.print') as mock_print:
            main()
            mock_search.assert_called_once_with('folder', '.*\\.txt$')
    
    @patch('sys.argv', ['cli.py', 'adddate', 'file.txt'])
    @patch('cli.add_creation_date_to_filename')
    def test_adddate_command(self, mock_adddate):
        mock_adddate.return_value = [('old.txt', 'new.txt')]
        with patch('builtins.print') as mock_print:
            main()
            mock_adddate.assert_called_once_with('file.txt', False)
    
    @patch('sys.argv', ['cli.py', 'adddate', 'folder', '--recursive'])
    @patch('cli.add_creation_date_to_filename')
    def test_adddate_command_recursive(self, mock_adddate):
        mock_adddate.return_value = []
        with patch('builtins.print') as mock_print:
            main()
            mock_adddate.assert_called_once_with('folder', True)
    
    @patch('sys.argv', ['cli.py', 'analyse', 'folder'])
    @patch('cli.analyse_folder_size')
    @patch('cli.format_analysis_result')
    def test_analyse_command(self, mock_format, mock_analyse):
        mock_analyse.return_value = {'total_size_formatted': '10MB'}
        mock_format.return_value = "formatted result"
        with patch('builtins.print') as mock_print:
            main()
            mock_analyse.assert_called_once_with('folder')
    
    @patch('sys.argv', ['cli.py'])
    def test_no_command(self):
        with patch('argparse.ArgumentParser.print_help') as mock_help:
            with self.assertRaises(SystemExit):
                main()


if __name__ == '__main__':
    unittest.main()