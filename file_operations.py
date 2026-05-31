import os
import shutil
import re
from datetime import datetime
from pathlib import Path


def copy_file(source: str, destination: str) -> bool:
    """
    Копирует файл из source в destination
    """
    try:
        if not os.path.exists(source):
            raise FileNotFoundError(f"Файл {source} не найден")
        if os.path.isdir(source):
            raise IsADirectoryError(f"{source} - это папка, а не файл")
        
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        raise e


def delete_path(path: str, recursive: bool = False) -> bool:
    """
    Удаляет файл или папку
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Путь {path} не найден")
        
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            if recursive:
                shutil.rmtree(path)
            else:
                # Удаляем только пустую папку
                os.rmdir(path)
        return True
    except Exception as e:
        raise e


def count_files_in_folder(path: str) -> int:
    """
    Подсчитывает количество файлов в папке (включая вложенные)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"{path} - это не папка")
    
    count = 0
    for root, dirs, files in os.walk(path):
        count += len(files)
    return count


def find_files_by_pattern(path: str, pattern: str) -> list:
    """
    Ищет файлы в папке (включая вложенные) по регулярному выражению
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"{path} - это не папка")
    
    regex = re.compile(pattern)
    matches = []
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if regex.search(file):
                full_path = os.path.join(root, file)
                matches.append(full_path)
    
    return matches


def add_creation_date_to_filename(path: str, recursive: bool = False) -> list:
    """
    Добавляет в название файла дату его создания
    Если выбрана папка - во все файлы в папке
    Если recursive=True - во все файлы на всех уровнях вложения
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден")
    
    renamed_files = []
    
    def process_file(file_path: str):
        try:
            # Получаем дату создания файла
            stat = os.stat(file_path)
            # На Windows это время создания, на Unix - время изменения метаданных
            creation_timestamp = stat.st_ctime
            creation_date = datetime.fromtimestamp(creation_timestamp).strftime("%Y%m%d")
            
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            
            # Новое имя с датой
            new_name = f"{name}_{creation_date}{ext}"
            new_path = os.path.join(dir_name, new_name)
            
            # Если файл с таким именем уже существует, добавляем суффикс
            counter = 1
            while os.path.exists(new_path):
                new_name = f"{name}_{creation_date}_{counter}{ext}"
                new_path = os.path.join(dir_name, new_name)
                counter += 1
            
            os.rename(file_path, new_path)
            renamed_files.append((file_path, new_path))
        except Exception as e:
            raise Exception(f"Ошибка при обработке {file_path}: {str(e)}")
    
    if os.path.isfile(path):
        process_file(path)
    elif os.path.isdir(path):
        if recursive:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    process_file(file_path)
        else:
            # Только файлы в корне папки
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    process_file(item_path)
    
    return renamed_files


def analyse_folder_size(path: str) -> dict:
    """
    Анализирует все вложенные папки и файлы и возвращает информацию о размерах
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"{path} - это не папка")
    
    def get_size(file_path: str) -> int:
        return os.path.getsize(file_path)
    
    def format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"
    
    result = {
        'path': path,
        'total_size': 0,
        'items': []
    }
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                size = get_size(item_path)
                result['total_size'] += size
                result['items'].append({
                    'name': item,
                    'path': item_path,
                    'size': size,
                    'type': 'file'
                })
            elif os.path.isdir(item_path):
                folder_result = analyse_folder_size(item_path)
                result['total_size'] += folder_result['total_size']
                result['items'].append({
                    'name': item,
                    'path': item_path,
                    'size': folder_result['total_size'],
                    'type': 'folder',
                    'children': folder_result['items']
                })
    except Exception as e:
        raise Exception(f"Ошибка при анализе: {str(e)}")
    
    result['total_size_formatted'] = format_size(result['total_size'])
    return result


def format_analysis_result(result: dict, indent: int = 0) -> str:
    """
    Форматирует результат анализа для вывода
    """
    lines = []
    prefix = "  " * indent
    lines.append(f"{prefix}- {os.path.basename(result['path'])}: {result['total_size_formatted']}")
    
    for item in result['items']:
        if item['type'] == 'file':
            size_formatted = format_size(item['size'])
            lines.append(f"{prefix}  - {item['name']}: {size_formatted}")
        else:
            lines.append(format_analysis_result(item, indent + 1))
    
    return "\n".join(lines)