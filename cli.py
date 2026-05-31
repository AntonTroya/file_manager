#!/usr/bin/env python3
import argparse
import sys
import os
from file_operations import (
    copy_file, delete_path, count_files_in_folder,
    find_files_by_pattern, add_creation_date_to_filename,
    analyse_folder_size, format_analysis_result
)


def main():
    parser = argparse.ArgumentParser(
        description="File Manager - Утилита для управления файлами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python cli.py copy test.txt dest.txt
  python cli.py delete folder_name --recursive
  python cli.py count /path/to/folder
  python cli.py search /path/to/folder ".*\\.txt$"
  python cli.py adddate file.txt
  python cli.py analyse /path/to/folder
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда copy
    copy_parser = subparsers.add_parser('copy', help='Копировать файл')
    copy_parser.add_argument('source', help='Исходный файл')
    copy_parser.add_argument('destination', help='Путь назначения')
    
    # Команда delete
    delete_parser = subparsers.add_parser('delete', help='Удалить файл или папку')
    delete_parser.add_argument('path', help='Путь для удаления')
    delete_parser.add_argument('--recursive', '-r', action='store_true', help='Рекурсивное удаление папки')
    
    # Команда count
    count_parser = subparsers.add_parser('count', help='Подсчитать количество файлов в папке')
    count_parser.add_argument('path', help='Путь к папке')
    
    # Команда search
    search_parser = subparsers.add_parser('search', help='Поиск файлов по регулярному выражению')
    search_parser.add_argument('path', help='Путь к папке')
    search_parser.add_argument('pattern', help='Регулярное выражение для поиска')
    
    # Команда adddate
    adddate_parser = subparsers.add_parser('adddate', help='Добавить дату создания в имя файла')
    adddate_parser.add_argument('path', help='Файл или папка')
    adddate_parser.add_argument('--recursive', '-r', action='store_true', help='Рекурсивно для всех вложенных файлов')
    
    # Команда analyse
    analyse_parser = subparsers.add_parser('analyse', help='Анализ размера файлов в папке')
    analyse_parser.add_argument('path', help='Путь к папке')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'copy':
            copy_file(args.source, args.destination)
            print(f"Файл скопирован: {args.source} -> {args.destination}")
        
        elif args.command == 'delete':
            delete_path(args.path, args.recursive)
            print(f"Удалено: {args.path}")
        
        elif args.command == 'count':
            count = count_files_in_folder(args.path)
            print(f"Количество файлов в папке {args.path}: {count}")
        
        elif args.command == 'search':
            results = find_files_by_pattern(args.path, args.pattern)
            print(f"Найдено файлов: {len(results)}")
            for r in results:
                print(f"  {r}")
        
        elif args.command == 'adddate':
            renamed = add_creation_date_to_filename(args.path, args.recursive)
            print(f"Переименовано файлов: {len(renamed)}")
            for old, new in renamed:
                print(f"  {os.path.basename(old)} -> {os.path.basename(new)}")
        
        elif args.command == 'analyse':
            result = analyse_folder_size(args.path)
            formatted = format_analysis_result(result)
            print(formatted)
            print(f"\nОбщий размер: {result['total_size_formatted']}")
    
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()