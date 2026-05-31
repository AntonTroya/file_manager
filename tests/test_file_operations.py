import unittest
import os
import tempfile
import shutil
from datetime import datetime
from file_operations import (
    copy_file, delete_path, count_files_in_folder,
    find_files_by_pattern, add_creation_date_to_filename,
    analyse_folder_size
)


class TestFileOperations(unittest.TestCase):
    
    def setUp(self):
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")
        
        self.sub_dir = os.path.join(self.test_dir, "subdir")
        os.mkdir(self.sub_dir)
        self.sub_file = os.path.join(self.sub_dir, "subtest.txt")
        with open(self.sub_file, "w") as f:
            f.write("sub content")
    
    def tearDown(self):
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)
    
    def test_copy_file(self):
        dest = os.path.join(self.test_dir, "copy.txt")
        copy_file(self.test_file, dest)
        self.assertTrue(os.path.exists(dest))
        with open(dest, "r") as f:
            self.assertEqual(f.read(), "test content")
    
    def test_copy_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            copy_file("nonexistent.txt", "dest.txt")
    
    def test_delete_file(self):
        delete_path(self.test_file)
        self.assertFalse(os.path.exists(self.test_file))
    
    def test_delete_folder_empty(self):
        empty_dir = os.path.join(self.test_dir, "empty")
        os.mkdir(empty_dir)
        delete_path(empty_dir)
        self.assertFalse(os.path.exists(empty_dir))
    
    def test_delete_folder_recursive(self):
        delete_path(self.sub_dir, recursive=True)
        self.assertFalse(os.path.exists(self.sub_dir))
    
    def test_count_files_in_folder(self):
        count = count_files_in_folder(self.test_dir)
        self.assertEqual(count, 2)  # test.txt и subtest.txt
    
    def test_count_files_in_file(self):
        with self.assertRaises(NotADirectoryError):
            count_files_in_folder(self.test_file)
    
    def test_find_files_by_pattern(self):
        results = find_files_by_pattern(self.test_dir, r".*\.txt$")
        self.assertEqual(len(results), 2)
        self.assertTrue(any(self.test_file in r for r in results))
        self.assertTrue(any(self.sub_file in r for r in results))
    
    def test_find_files_by_pattern_none(self):
        results = find_files_by_pattern(self.test_dir, r".*\.py$")
        self.assertEqual(len(results), 0)
    
    def test_add_date_to_file(self):
        renamed = add_creation_date_to_filename(self.test_file)
        self.assertEqual(len(renamed), 1)
        old, new = renamed[0]
        self.assertTrue(os.path.exists(new))
        self.assertFalse(os.path.exists(old))
    
    def test_add_date_to_folder_non_recursive(self):
        renamed = add_creation_date_to_filename(self.test_dir, recursive=False)
        # Только файлы в корне, не включая subdir
        self.assertEqual(len(renamed), 1)
    
    def test_add_date_to_folder_recursive(self):
        renamed = add_creation_date_to_filename(self.test_dir, recursive=True)
        self.assertEqual(len(renamed), 2)
    
    def test_analyse_folder_size(self):
        result = analyse_folder_size(self.test_dir)
        self.assertGreater(result['total_size'], 0)
        self.assertEqual(len(result['items']), 2)
        self.assertIn('total_size_formatted', result)


if __name__ == '__main__':
    unittest.main()