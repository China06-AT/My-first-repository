import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
from image_certificate_generator import ImageCertificateGenerator

class CoordinateEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор координат для сертификатов")
        self.root.geometry("1000x700")
        
        # Инициализация генератора сертификатов
        self.generator = ImageCertificateGenerator()
        
        # Получение текущих координат из класса генератора
        self.coordinates = self.generator.COORDINATES.copy()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Путь к последнему сгенерированному сертификату
        self.last_generated_file = None
        
    def create_widgets(self):
        # Создаем главный фрейм с вкладками
        tab_control = ttk.Notebook(self.root)
        
        # Вкладка для редактирования координат
        tab_coords = ttk.Frame(tab_control)
        tab_control.add(tab_coords, text="Координаты")
        
        # Вкладка для предпросмотра
        tab_preview = ttk.Frame(tab_control)
        tab_control.add(tab_preview, text="Предпросмотр")
        
        tab_control.pack(expand=1, fill="both")
        
        # ===== Вкладка координат =====
        # Фрейм для выбора типа сертификата
        cert_frame = ttk.LabelFrame(tab_coords, text="Тип сертификата")
        cert_frame.pack(fill="x", padx=10, pady=5)
        
        self.cert_type = tk.StringVar(value="OHRANA_TRUDA")
        ttk.Radiobutton(cert_frame, text="Безопасность и охрана труда", 
                       variable=self.cert_type, value="OHRANA_TRUDA", 
                       command=self.update_coordinate_view).pack(side="left", padx=5)
        ttk.Radiobutton(cert_frame, text="Электробезопасность", 
                       variable=self.cert_type, value="ELECTRO", 
                       command=self.update_coordinate_view).pack(side="left", padx=5)
        
        # Фрейм для отображения и редактирования координат
        coords_frame = ttk.LabelFrame(tab_coords, text="Координаты полей")
        coords_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаем фреймы для левой и правой сторон
        left_frame = ttk.LabelFrame(coords_frame, text="Левая сторона")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        right_frame = ttk.LabelFrame(coords_frame, text="Правая сторона")
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Контейнеры для полей ввода
        self.left_entries = {}
        self.right_entries = {}
        
        # Кнопки для сохранения и сброса
        btn_frame = ttk.Frame(tab_coords)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Сохранить координаты", 
                  command=self.save_coordinates).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сбросить к стандартным", 
                  command=self.reset_coordinates).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сохранить в JSON", 
                  command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить из JSON", 
                  command=self.load_from_json).pack(side="left", padx=5)
        
        # ===== Вкладка предпросмотра =====
        preview_frame = ttk.Frame(tab_preview)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Фрейм для тестовых данных
        test_data_frame = ttk.LabelFrame(preview_frame, text="Тестовые данные для генерации")
        test_data_frame.pack(fill="x", padx=10, pady=5)
        
        # Поля для тестовых данных
        ttk.Label(test_data_frame, text="ФИО:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.test_fullname = ttk.Entry(test_data_frame, width=30)
        self.test_fullname.insert(0, "Тестовый Пользователь")
        self.test_fullname.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(test_data_frame, text="Организация:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.test_workplace = ttk.Entry(test_data_frame, width=30)
        self.test_workplace.insert(0, "ООО Тест")
        self.test_workplace.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(test_data_frame, text="Должность:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.test_job_title = ttk.Entry(test_data_frame, width=30)
        self.test_job_title.insert(0, "Инженер")
        self.test_job_title.grid(row=2, column=1, padx=5, pady=2)
        
        # Кнопки для генерации
        gen_btn_frame = ttk.Frame(preview_frame)
        gen_btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(gen_btn_frame, text="Сгенерировать тестовый сертификат", 
                  command=lambda: self.generate_test_certificate(with_grid=True)).pack(side="left", padx=5)
        ttk.Button(gen_btn_frame, text="Сгенерировать без сетки", 
                  command=lambda: self.generate_test_certificate(with_grid=False)).pack(side="left", padx=5)
        ttk.Button(gen_btn_frame, text="Открыть последний сертификат", 
                  command=self.open_last_certificate).pack(side="left", padx=5)
        
        # Настройки сетки
        grid_frame = ttk.LabelFrame(preview_frame, text="Настройки координатной сетки")
        grid_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(grid_frame, text="Шаг основной сетки:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.grid_spacing = ttk.Spinbox(grid_frame, from_=5, to=50, width=5)
        self.grid_spacing.insert(0, "10")
        self.grid_spacing.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(grid_frame, text="Шаг дополнительной сетки:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.minor_grid = ttk.Spinbox(grid_frame, from_=0, to=10, width=5)
        self.minor_grid.insert(0, "2")
        self.minor_grid.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(grid_frame, text="Создать координатную сетку", 
                  command=self.create_coordinate_grid).pack(side="left", padx=5, pady=5)
        
        # Обновляем отображение координат
        self.update_coordinate_view()
    
    def update_coordinate_view(self):
        """Обновляет отображение координат на основе выбранного типа сертификата"""
        cert_type = self.cert_type.get()
        
        # Очистка предыдущих полей
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for entry_widget in child.winfo_children():
                            entry_widget.destroy()
        
        # Очистка словарей с полями ввода
        self.left_entries.clear()
        self.right_entries.clear()
        
        # Получаем родительские фреймы
        left_frame = None
        right_frame = None
        
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.winfo_children():
                    for frame in tab.winfo_children():
                        if isinstance(frame, ttk.LabelFrame) and frame.winfo_children():
                            for child in frame.winfo_children():
                                if isinstance(child, ttk.LabelFrame):
                                    if "Левая" in child["text"]:
                                        left_frame = child
                                    elif "Правая" in child["text"]:
                                        right_frame = child
        
        if not left_frame or not right_frame:
            return
        
        # Определяем, какие координаты использовать
        if cert_type == "OHRANA_TRUDA":
            left_coords = self.coordinates.get('OHRANA_TRUDA', {}).get('LEFT', {})
            right_coords = self.coordinates.get('OHRANA_TRUDA', {}).get('RIGHT', {})
        else:
            left_coords = self.coordinates.get('LEFT', {})
            right_coords = self.coordinates.get('RIGHT', {})
        
        # Создаем поля для левой стороны
        row = 0
        for key, (x, y) in left_coords.items():
            ttk.Label(left_frame, text=f"{key}:").grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            x_entry = ttk.Entry(left_frame, width=5)
            x_entry.insert(0, str(x))
            x_entry.grid(row=row, column=1, padx=2, pady=2)
            
            ttk.Label(left_frame, text="X").grid(row=row, column=2)
            
            y_entry = ttk.Entry(left_frame, width=5)
            y_entry.insert(0, str(y))
            y_entry.grid(row=row, column=3, padx=2, pady=2)
            
            ttk.Label(left_frame, text="Y").grid(row=row, column=4)
            
            self.left_entries[key] = (x_entry, y_entry)
            row += 1
        
        # Создаем поля для правой стороны
        row = 0
        for key, (x, y) in right_coords.items():
            ttk.Label(right_frame, text=f"{key}:").grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            x_entry = ttk.Entry(right_frame, width=5)
            x_entry.insert(0, str(x))
            x_entry.grid(row=row, column=1, padx=2, pady=2)
            
            ttk.Label(right_frame, text="X").grid(row=row, column=2)
            
            y_entry = ttk.Entry(right_frame, width=5)
            y_entry.insert(0, str(y))
            y_entry.grid(row=row, column=3, padx=2, pady=2)
            
            ttk.Label(right_frame, text="Y").grid(row=row, column=4)
            
            self.right_entries[key] = (x_entry, y_entry)
            row += 1
    
    def save_coordinates(self):
        """Сохраняет изменения координат в объект генератора"""
        cert_type = self.cert_type.get()
        
        # Обновляем координаты в зависимости от типа сертификата
        if cert_type == "OHRANA_TRUDA":
            for key, (x_entry, y_entry) in self.left_entries.items():
                try:
                    x = int(x_entry.get())
                    y = int(y_entry.get())
                    self.coordinates['OHRANA_TRUDA']['LEFT'][key] = (x, y)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для {key}")
                    return
            
            for key, (x_entry, y_entry) in self.right_entries.items():
                try:
                    x = int(x_entry.get())
                    y = int(y_entry.get())
                    self.coordinates['OHRANA_TRUDA']['RIGHT'][key] = (x, y)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для {key}")
                    return
        else:
            for key, (x_entry, y_entry) in self.left_entries.items():
                try:
                    x = int(x_entry.get())
                    y = int(y_entry.get())
                    self.coordinates['LEFT'][key] = (x, y)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для {key}")
                    return
            
            for key, (x_entry, y_entry) in self.right_entries.items():
                try:
                    x = int(x_entry.get())
                    y = int(y_entry.get())
                    self.coordinates['RIGHT'][key] = (x, y)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректное значение для {key}")
                    return
        
        # Обновляем координаты в генераторе
        self.generator.COORDINATES = self.coordinates
        
        messagebox.showinfo("Успех", "Координаты успешно сохранены")
    
    def reset_coordinates(self):
        """Сбрасывает координаты к исходным значениям"""
        # Создаем новый экземпляр генератора для получения стандартных координат
        temp_generator = ImageCertificateGenerator()
        self.coordinates = temp_generator.COORDINATES.copy()
        
        # Обновляем отображение
        self.update_coordinate_view()
        
        messagebox.showinfo("Сброс", "Координаты сброшены к стандартным значениям")
    
    def save_to_json(self):
        """Сохраняет координаты в JSON файл"""
        try:
            # Преобразуем координаты в формат для сохранения
            save_data = {}
            
            for section_key, section_value in self.coordinates.items():
                if isinstance(section_value, dict):
                    save_data[section_key] = {}
                    for subsection_key, subsection_value in section_value.items():
                        if isinstance(subsection_value, dict):
                            save_data[section_key][subsection_key] = {}
                            for key, value in subsection_value.items():
                                if isinstance(value, tuple):
                                    save_data[section_key][subsection_key][key] = list(value)
                                else:
                                    save_data[section_key][subsection_key][key] = value
                        else:
                            if isinstance(subsection_value, tuple):
                                save_data[section_key][subsection_key] = list(subsection_value)
                            else:
                                save_data[section_key][subsection_key] = subsection_value
                else:
                    if isinstance(section_value, tuple):
                        save_data[section_key] = list(section_value)
                    else:
                        save_data[section_key] = section_value
            
            # Запрашиваем путь для сохранения
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON файлы", "*.json")],
                title="Сохранить координаты"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Успех", f"Координаты сохранены в {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить координаты: {str(e)}")
    
    def load_from_json(self):
        """Загружает координаты из JSON файла"""
        try:
            # Запрашиваем путь к файлу
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON файлы", "*.json")],
                title="Загрузить координаты"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                load_data = json.load(f)
            
            # Преобразуем загруженные данные в формат координат
            for section_key, section_value in load_data.items():
                if isinstance(section_value, dict):
                    if section_key not in self.coordinates:
                        self.coordinates[section_key] = {}
                        
                    for subsection_key, subsection_value in section_value.items():
                        if isinstance(subsection_value, dict):
                            if subsection_key not in self.coordinates[section_key]:
                                self.coordinates[section_key][subsection_key] = {}
                                
                            for key, value in subsection_value.items():
                                if isinstance(value, list):
                                    self.coordinates[section_key][subsection_key][key] = tuple(value)
                                else:
                                    self.coordinates[section_key][subsection_key][key] = value
                        else:
                            if isinstance(subsection_value, list):
                                self.coordinates[section_key][subsection_key] = tuple(subsection_value)
                            else:
                                self.coordinates[section_key][subsection_key] = subsection_value
                else:
                    if isinstance(section_value, list):
                        self.coordinates[section_key] = tuple(section_value)
                    else:
                        self.coordinates[section_key] = section_value
            
            # Обновляем отображение
            self.update_coordinate_view()
            
            messagebox.showinfo("Успех", f"Координаты загружены из {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить координаты: {str(e)}")
    
    def generate_test_certificate(self, with_grid=True):
        """Генерирует тестовый сертификат с текущими координатами"""
        try:
            # Сначала сохраняем изменения координат
            self.save_coordinates()
            
            # Получаем тестовые данные
            fullname = self.test_fullname.get()
            workplace = self.test_workplace.get()
            job_title = self.test_job_title.get()
            
            if not fullname or not workplace or not job_title:
                messagebox.showwarning("Предупреждение", "Заполните все тестовые данные")
                return
            
            # Определяем тип сертификата
            cert_type = self.cert_type.get()
            
            # Подготавливаем данные для генерации
            now = datetime.now()
            next_year = now + timedelta(days=365)
            
            if cert_type == "OHRANA_TRUDA":
                position = 'Безопасность и Охрана труда'
                qualification_group = ''
            else:
                position = 'Курс по электробезопасности'
                qualification_group = '3'
            
            # Данные для сертификата
            data = {
                'position': position,
                'fullname': fullname,
                'workplace': workplace,
                'job_title': job_title,
                'qualification_group': qualification_group,
                'cert_date': now,
                'next_date': next_year
            }
            
            # Определяем плотность сетки
            grid_density = 20
            if with_grid:
                try:
                    grid_density = int(self.grid_spacing.get())
                except ValueError:
                    grid_density = 20
            
            # Генерируем сертификат
            success, files = self.generator.generate_document(
                data, 
                debug_mode=with_grid, 
                grid_density=grid_density
            )
            
            if success and files:
                self.last_generated_file = files[0]
                messagebox.showinfo("Успех", f"Сертификат успешно создан: {self.last_generated_file}")
                
                # Открываем сертификат
                self.open_last_certificate()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать сертификат")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать сертификат: {str(e)}")
    
    def create_coordinate_grid(self):
        """Создает отдельную координатную сетку для шаблона"""
        try:
            # Получаем параметры сетки
            try:
                grid_spacing = int(self.grid_spacing.get())
                minor_grid = int(self.minor_grid.get())
            except ValueError:
                grid_spacing = 20
                minor_grid = 5
            
            # Определяем тип сертификата
            cert_type = self.cert_type.get()
            
            if cert_type == "OHRANA_TRUDA":
                template_name = 'ohrana_truda'
            else:
                template_name = 'korotchka'
            
            # Создаем сетку
            grid_path = self.generator.create_detailed_grid(
                template_name=template_name,
                grid_spacing=grid_spacing,
                minor_grid_step=minor_grid,
                grid_opacity=80,
                show_labels=True
            )
            
            if grid_path:
                self.last_generated_file = grid_path
                messagebox.showinfo("Успех", f"Координатная сетка создана: {grid_path}")
                
                # Открываем файл
                self.open_last_certificate()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать координатную сетку")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать координатную сетку: {str(e)}")
    
    def open_last_certificate(self):
        """Открывает последний сгенерированный файл"""
        if self.last_generated_file and os.path.exists(self.last_generated_file):
            try:
                os.startfile(self.last_generated_file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
        else:
            messagebox.showwarning("Предупреждение", "Нет последнего сгенерированного файла")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoordinateEditor(root)
    root.mainloop() 