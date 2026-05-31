import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path

from file_operations import (
    copy_file, delete_path, count_files_in_folder,
    find_files_by_pattern, add_creation_date_to_filename,
    analyse_folder_size, format_analysis_result
)


class FileManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager - Управление файлами")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        
        # Создание интерфейса
        self.create_widgets()
        
        # Перенаправление stdout для логирования
        self.setup_logging()
    
    def setup_logging(self):
        """Настройка перенаправления вывода в текстовое поле"""
        class TextRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget
            
            def write(self, str):
                self.text_widget.insert(tk.END, str)
                self.text_widget.see(tk.END)
                self.text_widget.update_idletasks()
            
            def flush(self):
                pass
        
        sys.stdout = TextRedirector(self.log_text)
        sys.stderr = TextRedirector(self.log_text)
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Главный контейнер с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладки для каждой операции
        self.create_copy_tab()
        self.create_delete_tab()
        self.create_count_tab()
        self.create_search_tab()
        self.create_date_tab()
        self.create_analyse_tab()
        
        # Вкладка с логами
        self.create_log_tab()
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_copy_tab(self):
        """Вкладка копирования файла"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Копировать файл")
        
        # Tooltip
        self.create_tooltip_text(tab, "Копирование файла из одного места в другое")
        
        # Источник
        ttk.Label(tab, text="Исходный файл:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.copy_source_entry = ttk.Entry(tab, width=60)
        self.copy_source_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор...", command=lambda: self.browse_file(self.copy_source_entry)).grid(row=0, column=2, padx=5, pady=10)
        
        # Назначение
        ttk.Label(tab, text="Путь назначения:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.copy_dest_entry = ttk.Entry(tab, width=60)
        self.copy_dest_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор (файл)...", command=lambda: self.browse_file_save(self.copy_dest_entry)).grid(row=1, column=2, padx=5, pady=10)
        
        # Кнопка выполнения
        ttk.Button(tab, text="Копировать", command=self.execute_copy).grid(row=2, column=1, pady=20)
        
        # Помощь
        help_text = "Совет: Выберите исходный файл и укажите путь для копирования"
        ttk.Label(tab, text=help_text, foreground="gray").grid(row=3, column=0, columnspan=3, pady=10)
    
    def create_delete_tab(self):
        """Вкладка удаления"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🗑 Удалить")
        
        self.create_tooltip_text(tab, "Удаление файла или папки")
        
        ttk.Label(tab, text="Путь для удаления:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.delete_entry = ttk.Entry(tab, width=60)
        self.delete_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор...", command=lambda: self.browse_path(self.delete_entry)).grid(row=0, column=2, padx=5, pady=10)
        
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Рекурсивное удаление (для папок)", variable=self.recursive_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
        
        ttk.Button(tab, text="Удалить", command=self.execute_delete).grid(row=2, column=1, pady=20)
        
        ttk.Label(tab, text="Внимание: Удаление без возможности восстановления!", foreground="red").grid(row=3, column=0, columnspan=3, pady=10)
    
    def create_count_tab(self):
        """Вкладка подсчета файлов"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔢 Подсчет файлов")
        
        self.create_tooltip_text(tab, "Подсчет количества файлов в папке (включая вложенные)")
        
        ttk.Label(tab, text="Папка для анализа:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.count_entry = ttk.Entry(tab, width=60)
        self.count_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор...", command=lambda: self.browse_folder(self.count_entry)).grid(row=0, column=2, padx=5, pady=10)
        
        self.count_result = tk.StringVar()
        ttk.Label(tab, text="Результат:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        ttk.Label(tab, textvariable=self.count_result, foreground="blue").grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Button(tab, text="Подсчитать", command=self.execute_count).grid(row=2, column=1, pady=20)
    
    def create_search_tab(self):
        """Вкладка поиска файлов"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Поиск файлов")
        
        self.create_tooltip_text(tab, "Поиск файлов по регулярному выражению")
        
        ttk.Label(tab, text="Папка для поиска:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.search_dir_entry = ttk.Entry(tab, width=60)
        self.search_dir_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор...", command=lambda: self.browse_folder(self.search_dir_entry)).grid(row=0, column=2, padx=5, pady=10)
        
        ttk.Label(tab, text="Регулярное выражение:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.pattern_entry = ttk.Entry(tab, width=60)
        self.pattern_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Label(tab, text="Пример: .*\\.txt$ - все txt файлы", foreground="gray").grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Результаты
        ttk.Label(tab, text="Найденные файлы:").grid(row=3, column=0, sticky=tk.NW, padx=10, pady=10)
        self.search_results = scrolledtext.ScrolledText(tab, width=80, height=15)
        self.search_results.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Button(tab, text="Найти", command=self.execute_search).grid(row=4, column=1, pady=20)
    
    def create_date_tab(self):
        """Вкладка добавления даты создания"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📅 Добавить дату")
        
        self.create_tooltip_text(tab, "Добавление даты создания в имя файла")
        
        ttk.Label(tab, text="Файл/Папка:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.date_path_entry = ttk.Entry(tab, width=60)
        self.date_path_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор...", command=lambda: self.browse_path(self.date_path_entry)).grid(row=0, column=2, padx=5, pady=10)
        
        self.recursive_date_var = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Рекурсивно (для всех вложенных файлов)", variable=self.recursive_date_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
        
        self.date_result = scrolledtext.ScrolledText(tab, width=80, height=15)
        self.date_result.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Button(tab, text="Переименовать", command=self.execute_add_date).grid(row=3, column=1, pady=20)
    
    def create_analyse_tab(self):
        """Вкладка анализа размера"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Анализ размера")
        
        self.create_tooltip_text(tab, "Анализ размеров файлов и папок")
        
        ttk.Label(tab, text="Папка для анализа:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.analyse_entry = ttk.Entry(tab, width=60)
        self.analyse_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(tab, text="Обзор...", command=lambda: self.browse_folder(self.analyse_entry)).grid(row=0, column=2, padx=5, pady=10)
        
        self.analyse_results = scrolledtext.ScrolledText(tab, width=80, height=20)
        self.analyse_results.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W+tk.E)
        
        ttk.Button(tab, text="Анализировать", command=self.execute_analyse).grid(row=2, column=1, pady=20)
    
    def create_log_tab(self):
        """Вкладка с логами"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📝 Логи")
        
        self.log_text = scrolledtext.ScrolledText(tab, width=90, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(tab, text="Очистить логи", command=self.clear_logs).pack(pady=5)
    
    def create_tooltip_text(self, widget, text):
        """Создание всплывающей подсказки"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack()
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def browse_file(self, entry):
        """Выбор файла"""
        filename = filedialog.askopenfilename(title="Выберите файл")
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def browse_file_save(self, entry):
        """Выбор места сохранения"""
        filename = filedialog.asksaveasfilename(title="Сохранить как")
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def browse_folder(self, entry):
        """Выбор папки"""
        folder = filedialog.askdirectory(title="Выберите папку")
        if folder:
            entry.delete(0, tk.END)
            entry.insert(0, folder)
    
    def browse_path(self, entry):
        """Выбор файла или папки"""
        path = filedialog.askopenfilename(title="Выберите файл")
        if not path:
            path = filedialog.askdirectory(title="Выберите папку")
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)
    
    def update_status(self, message, is_error=False):
        """Обновление статус бара"""
        self.status_bar.config(text=message, foreground="red" if is_error else "black")
        self.root.update_idletasks()
    
    def run_in_thread(self, func, *args):
        """Запуск длительной операции в отдельном потоке"""
        def wrapper():
            try:
                self.update_status("Выполняется...")
                result = func(*args)
                self.update_status("Готово")
                return result
            except Exception as e:
                self.update_status(f"Ошибка: {str(e)}", is_error=True)
                messagebox.showerror("Ошибка", str(e))
            finally:
                self.root.after(0, lambda: None)
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
    
    def execute_copy(self):
        source = self.copy_source_entry.get()
        dest = self.copy_dest_entry.get()
        
        if not source or not dest:
            messagebox.showwarning("Предупреждение", "Заполните оба поля")
            return
        
        def copy():
            copy_file(source, dest)
            print(f"✓ Файл скопирован: {source} -> {dest}")
        
        self.run_in_thread(copy)
    
    def execute_delete(self):
        path = self.delete_entry.get()
        if not path:
            messagebox.showwarning("Предупреждение", "Укажите путь")
            return
        
        recursive = self.recursive_var.get()
        
        if not messagebox.askyesno("Подтверждение", f"Удалить {path}? Это действие необратимо!"):
            return
        
        def delete():
            delete_path(path, recursive)
            print(f"✓ Удалено: {path}")
        
        self.run_in_thread(delete)
    
    def execute_count(self):
        path = self.count_entry.get()
        if not path:
            messagebox.showwarning("Предупреждение", "Укажите папку")
            return
        
        def count():
            count = count_files_in_folder(path)
            self.count_result.set(str(count))
            print(f"✓ В папке {path} найдено файлов: {count}")
        
        self.run_in_thread(count)
    
    def execute_search(self):
        path = self.search_dir_entry.get()
        pattern = self.pattern_entry.get()
        
        if not path or not pattern:
            messagebox.showwarning("Предупреждение", "Заполните оба поля")
            return
        
        self.search_results.delete(1.0, tk.END)
        
        def search():
            results = find_files_by_pattern(path, pattern)
            self.root.after(0, lambda: self.display_search_results(results))
            print(f"✓ Найдено файлов по шаблону '{pattern}': {len(results)}")
        
        self.run_in_thread(search)
    
    def display_search_results(self, results):
        self.search_results.delete(1.0, tk.END)
        if results:
            for r in results:
                self.search_results.insert(tk.END, f"• {r}\n")
        else:
            self.search_results.insert(tk.END, "Файлы не найдены")
    
    def execute_add_date(self):
        path = self.date_path_entry.get()
        if not path:
            messagebox.showwarning("Предупреждение", "Укажите путь")
            return
        
        recursive = self.recursive_date_var.get()
        self.date_result.delete(1.0, tk.END)
        
        def add_date():
            renamed = add_creation_date_to_filename(path, recursive)
            self.root.after(0, lambda: self.display_rename_results(renamed))
            print(f"✓ Переименовано файлов: {len(renamed)}")
        
        self.run_in_thread(add_date)
    
    def display_rename_results(self, renamed):
        self.date_result.delete(1.0, tk.END)
        if renamed:
            self.date_result.insert(tk.END, "Переименованные файлы:\n")
            for old, new in renamed:
                self.date_result.insert(tk.END, f"• {os.path.basename(old)} → {os.path.basename(new)}\n")
        else:
            self.date_result.insert(tk.END, "Файлы не были переименованы")
    
    def execute_analyse(self):
        path = self.analyse_entry.get()
        if not path:
            messagebox.showwarning("Предупреждение", "Укажите папку")
            return
        
        self.analyse_results.delete(1.0, tk.END)
        
        def analyse():
            result = analyse_folder_size(path)
            formatted = format_analysis_result(result)
            self.root.after(0, lambda: self.display_analyse_results(formatted, result))
            print(f"✓ Анализ завершен. Общий размер: {result['total_size_formatted']}")
        
        self.run_in_thread(analyse)
    
    def display_analyse_results(self, formatted, result):
        self.analyse_results.delete(1.0, tk.END)
        self.analyse_results.insert(tk.END, f"Результат анализа папки:\n\n")
        self.analyse_results.insert(tk.END, formatted)
        self.analyse_results.insert(tk.END, f"\n\nОбщий размер: {result['total_size_formatted']}")
    
    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
        print("Логи очищены")


def main():
    root = tk.Tk()
    app = FileManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()