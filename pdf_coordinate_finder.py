import os
import sys
import json
import logging
import re
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import pymupdf

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFCoordinateFinder:
    def __init__(self, root, pdf_path=None):
        self.root = root
        self.root.title("PDF Coordinate Finder")
        self.root.geometry("1200x800")
        
        # Переменные
        self.pdf_path = pdf_path
        self.current_image = None
        self.image_tk = None
        self.zoom_factor = 1.0
        self.coordinates = {}
        self.current_template = "OHRANA_TRUDA"
        self.current_section = "LEFT"
        self.grid_visible = False
        self.grid_size = 20
        self.snap_to_grid = True
        
        # Создание интерфейса
        self.create_ui()
        
        # Если путь к PDF указан, загружаем его
        if self.pdf_path and os.path.exists(self.pdf_path):
            self.load_pdf(self.pdf_path)
    
    def create_ui(self):
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(top_frame, text="Открыть PDF", command=self.open_pdf).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Сохранить координаты", command=self.save_coordinates).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Загрузить координаты", command=self.load_coordinates).pack(side="left", padx=5)
        
        # Панель настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Первый ряд настроек
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(row1, text="Шаблон:").pack(side="left", padx=5)
        self.template_var = tk.StringVar(value=self.current_template)
        ttk.Entry(row1, textvariable=self.template_var, width=20).pack(side="left", padx=5)
        
        ttk.Label(row1, text="Секция:").pack(side="left", padx=5)
        self.section_var = tk.StringVar(value=self.current_section)
        ttk.Combobox(row1, textvariable=self.section_var, values=["LEFT", "RIGHT"], width=10).pack(side="left", padx=5)
        
        # Второй ряд настроек
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill="x", padx=5, pady=5)
        
        self.grid_var = tk.BooleanVar(value=self.grid_visible)
        ttk.Checkbutton(row2, text="Показать сетку", variable=self.grid_var, command=self.toggle_grid).pack(side="left", padx=5)
        
        ttk.Label(row2, text="Размер сетки:").pack(side="left", padx=5)
        self.grid_size_var = tk.StringVar(value=str(self.grid_size))
        ttk.Spinbox(row2, from_=5, to=50, increment=5, textvariable=self.grid_size_var, width=5, 
                   command=self.update_grid_size).pack(side="left", padx=5)
        
        self.snap_var = tk.BooleanVar(value=self.snap_to_grid)
        ttk.Checkbutton(row2, text="Привязка к сетке", variable=self.snap_var).pack(side="left", padx=5)
        
        ttk.Label(row2, text="Масштаб:").pack(side="left", padx=5)
        ttk.Button(row2, text="+", width=2, command=lambda: self.zoom(1.2)).pack(side="left")
        ttk.Button(row2, text="-", width=2, command=lambda: self.zoom(0.8)).pack(side="left", padx=5)
        ttk.Button(row2, text="100%", width=4, command=lambda: self.set_zoom(1.0)).pack(side="left")
        
        # Основная область с изображением
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Холст для отображения PDF
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(side="left", fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="gray")
        self.canvas.pack(fill="both", expand=True)
        
        # Добавляем скроллбары
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Привязываем события
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Панель координат
        coords_frame = ttk.LabelFrame(self.main_frame, text="Координаты")
        coords_frame.pack(side="right", fill="y", padx=5, pady=5, ipadx=5, ipady=5)
        
        ttk.Label(coords_frame, text="Текущие координаты:").pack(anchor="w", padx=5, pady=5)
        self.current_coords_label = ttk.Label(coords_frame, text="X: 0, Y: 0")
        self.current_coords_label.pack(anchor="w", padx=5, pady=5)
        
        ttk.Label(coords_frame, text="Название поля:").pack(anchor="w", padx=5, pady=5)
        self.field_name_var = tk.StringVar()
        ttk.Entry(coords_frame, textvariable=self.field_name_var, width=20).pack(padx=5, pady=5)
        
        ttk.Button(coords_frame, text="Добавить координату", command=self.add_coordinate).pack(padx=5, pady=5)
        
        # Список сохраненных координат
        ttk.Label(coords_frame, text="Сохраненные координаты:").pack(anchor="w", padx=5, pady=5)
        
        self.coords_list_frame = ttk.Frame(coords_frame)
        self.coords_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Текстовое поле для вывода кода
        ttk.Label(coords_frame, text="Код для вставки:").pack(anchor="w", padx=5, pady=5)
        
        code_frame = ttk.Frame(coords_frame)
        code_frame.pack(fill="x", padx=5, pady=5)
        
        self.code_text = tk.Text(code_frame, height=10, width=30, wrap="none")
        self.code_text.pack(side="left", fill="both")
        
        code_scroll = ttk.Scrollbar(code_frame, command=self.code_text.yview)
        code_scroll.pack(side="right", fill="y")
        
        self.code_text.configure(yscrollcommand=code_scroll.set)
        
        ttk.Button(coords_frame, text="Копировать код", command=self.copy_code).pack(padx=5, pady=5)
    
    def open_pdf(self):
        """Открывает диалог выбора PDF файла"""
        pdf_path = filedialog.askopenfilename(
            title="Выберите PDF файл",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]
        )
        
        if pdf_path:
            self.load_pdf(pdf_path)
    
    def load_pdf(self, pdf_path):
        """Загружает PDF файл и отображает его первую страницу"""
        try:
            self.pdf_path = pdf_path
            
            # Открываем PDF
            pdf_document = pymupdf.open(pdf_path)
            
            if len(pdf_document) > 0:
                # Получаем первую страницу
                page = pdf_document[0]
                
                # Создаем изображение с увеличенным разрешением
                zoom = 2.0  # Увеличиваем разрешение в 2 раза
                mat = pymupdf.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Конвертируем в PIL Image
                img_data = pix.samples
                img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
                
                # Сохраняем изображение
                self.current_image = img
                
                # Обновляем отображение
                self.update_image_display()
                
                # Закрываем PDF
                pdf_document.close()
                
                # Устанавливаем заголовок окна
                self.root.title(f"PDF Coordinate Finder - {os.path.basename(pdf_path)}")
                
                # Обновляем список координат
                self.update_coordinates_list()
                
            else:
                messagebox.showerror("Ошибка", "PDF файл не содержит страниц")
                
        except Exception as e:
            logger.error(f"Ошибка при загрузке PDF: {e}", exc_info=True)
            messagebox.showerror("Ошибка", f"Не удалось загрузить PDF: {str(e)}")
    
    def update_image_display(self):
        """Обновляет отображение изображения на холсте"""
        if self.current_image:
            # Применяем масштабирование
            width = int(self.current_image.width * self.zoom_factor)
            height = int(self.current_image.height * self.zoom_factor)
            
            # Изменяем размер изображения
            img_resized = self.current_image.resize((width, height), Image.LANCZOS)
            
            # Конвертируем в формат для Tkinter
            self.image_tk = ImageTk.PhotoImage(img_resized)
            
            # Очищаем холст
            self.canvas.delete("all")
            
            # Отображаем изображение
            self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
            
            # Настраиваем область прокрутки
            self.canvas.config(scrollregion=(0, 0, width, height))
            
            # Отображаем сетку, если нужно
            if self.grid_visible:
                self.draw_grid()
    
    def zoom(self, factor):
        """Изменяет масштаб изображения"""
        self.zoom_factor *= factor
        self.update_image_display()
    
    def set_zoom(self, factor):
        """Устанавливает конкретный масштаб"""
        self.zoom_factor = factor
        self.update_image_display()
    
    def toggle_grid(self):
        """Включает/выключает отображение сетки"""
        self.grid_visible = self.grid_var.get()
        self.update_image_display()
    
    def update_grid_size(self):
        """Обновляет размер сетки"""
        try:
            self.grid_size = int(self.grid_size_var.get())
            if self.grid_visible:
                self.update_image_display()
        except ValueError:
            pass
    
    def draw_grid(self):
        """Рисует координатную сетку на изображении"""
        if not self.current_image:
            return
        
        width = int(self.current_image.width * self.zoom_factor)
        height = int(self.current_image.height * self.zoom_factor)
        grid_size = int(self.grid_size * self.zoom_factor)
        
        # Рисуем вертикальные линии
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height, fill="blue", width=0.5)
            
            # Добавляем метки для каждой 5-й линии
            if x % (grid_size * 5) == 0:
                # Переводим координаты обратно в оригинальный масштаб для отображения
                orig_x = int(x / self.zoom_factor)
                self.canvas.create_text(x + 5, 10, text=str(orig_x), fill="blue", anchor="nw")
        
        # Рисуем горизонтальные линии
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y, fill="blue", width=0.5)
            
            # Добавляем метки для каждой 5-й линии
            if y % (grid_size * 5) == 0:
                # Переводим координаты обратно в оригинальный масштаб для отображения
                orig_y = int(y / self.zoom_factor)
                self.canvas.create_text(5, y + 5, text=str(orig_y), fill="blue", anchor="nw")
    
    def on_canvas_click(self, event):
        """Обрабатывает клик на холсте"""
        if not self.current_image:
            return
        
        # Получаем координаты с учетом прокрутки
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Переводим в оригинальный масштаб
        x = int(canvas_x / self.zoom_factor)
        y = int(canvas_y / self.zoom_factor)
        
        # Привязка к сетке, если включена
        if self.snap_var.get():
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size
        
        # Обновляем отображение координат
        self.current_coords_label.config(text=f"X: {x}, Y: {y}")
        
        # Фокус на поле ввода имени
        self.field_name_var.set("")
        # Находим виджет ввода имени поля и устанавливаем на него фокус
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.winfo_children():
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Entry) and grandchild.cget("textvariable") == str(self.field_name_var):
                                grandchild.focus_set()
                                return
    
    def on_canvas_motion(self, event):
        """Обрабатывает движение мыши по холсту"""
        if not self.current_image:
            return
        
        # Получаем координаты с учетом прокрутки
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Переводим в оригинальный масштаб
        x = int(canvas_x / self.zoom_factor)
        y = int(canvas_y / self.zoom_factor)
        
        # Привязка к сетке, если включена
        if self.snap_var.get():
            x = round(x / self.grid_size) * self.grid_size
            y = round(y / self.grid_size) * self.grid_size
        
        # Обновляем отображение координат
        self.current_coords_label.config(text=f"X: {x}, Y: {y}")
    
    def add_coordinate(self):
        """Добавляет текущую координату в список"""
        field_name = self.field_name_var.get().strip()
        if not field_name:
            messagebox.showwarning("Предупреждение", "Введите название поля")
            return
        
        # Получаем текущие координаты
        coords_text = self.current_coords_label.cget("text")
        match = re.match(r"X: (\d+), Y: (\d+)", coords_text)
        
        if not match:
            return
        
        x = int(match.group(1))
        y = int(match.group(2))
        
        # Обновляем текущие шаблон и секцию
        self.current_template = self.template_var.get().strip()
        self.current_section = self.section_var.get().strip()
        
        # Создаем структуру данных, если нужно
        if self.current_template not in self.coordinates:
            self.coordinates[self.current_template] = {}
        
        if self.current_section not in self.coordinates[self.current_template]:
            self.coordinates[self.current_template][self.current_section] = {}
        
        # Добавляем координату
        self.coordinates[self.current_template][self.current_section][field_name] = (x, y)
        
        # Обновляем список координат и код
        self.update_coordinates_list()
        self.update_code_output()
        
        # Очищаем поле ввода
        self.field_name_var.set("")
    
    def update_coordinates_list(self):
        """Обновляет список сохраненных координат"""
        # Очищаем текущий список
        for widget in self.coords_list_frame.winfo_children():
            widget.destroy()
        
        # Создаем новый список
        for template in self.coordinates:
            template_label = ttk.Label(self.coords_list_frame, text=f"Шаблон: {template}", font=("", 10, "bold"))
            template_label.pack(anchor="w", padx=5, pady=(10, 2))
            
            for section in self.coordinates[template]:
                section_label = ttk.Label(self.coords_list_frame, text=f"Секция: {section}", font=("", 9, "italic"))
                section_label.pack(anchor="w", padx=15, pady=(5, 2))
                
                for field, (x, y) in self.coordinates[template][section].items():
                    coord_frame = ttk.Frame(self.coords_list_frame)
                    coord_frame.pack(fill="x", padx=20, pady=1)
                    
                    ttk.Label(coord_frame, text=f"{field}: ({x}, {y})").pack(side="left")
                    
                    ttk.Button(
                        coord_frame, 
                        text="X", 
                        width=2, 
                        command=lambda t=template, s=section, f=field: self.delete_coordinate(t, s, f)
                    ).pack(side="right")
    
    def delete_coordinate(self, template, section, field):
        """Удаляет координату из списка"""
        if template in self.coordinates and section in self.coordinates[template]:
            if field in self.coordinates[template][section]:
                del self.coordinates[template][section][field]
                
                # Удаляем пустые секции и шаблоны
                if not self.coordinates[template][section]:
                    del self.coordinates[template][section]
                
                if not self.coordinates[template]:
                    del self.coordinates[template]
                
                # Обновляем список и код
                self.update_coordinates_list()
                self.update_code_output()
    
    def update_code_output(self):
        """Обновляет код для вставки в программу"""
        code = "COORDINATES = {\n"
        
        for template in self.coordinates:
            code += f"    # Координаты для шаблона {template}\n"
            code += f"    '{template}': {{\n"
            
            for section in self.coordinates[template]:
                code += f"        '{section}': {{\n"
                
                for field, (x, y) in self.coordinates[template][section].items():
                    description = self.get_field_description(field)
                    code += f"            '{field}': ({x}, {y}),  # {description}\n"
                
                code += "        },\n"
            
            code += "    },\n"
        
        code += "}"
        
        # Обновляем текстовое поле
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, code)
    
    def get_field_description(self, field):
        """Возвращает описание поля по его имени"""
        descriptions = {
            'protocol_number': 'Номер удостоверения',
            'workplace': 'Организация',
            'fullname': 'ФИО',
            'job_title': 'Должность',
            'group_text': 'Группа допуска',
            'cert_day': 'День выдачи',
            'cert_month': 'Месяц выдачи',
            'cert_year': 'Год выдачи',
            'cert_date': 'Дата проверки',
            'reason': 'Причина проверки',
            'group': 'Группа (римская)',
            'mark': 'Оценка',
            'next_date': 'Дата следующей проверки'
        }
        
        return descriptions.get(field, 'Пользовательское поле')
    
    def copy_code(self):
        """Копирует код в буфер обмена"""
        code = self.code_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("Копирование", "Код скопирован в буфер обмена")
    
    def save_coordinates(self):
        """Сохраняет координаты в JSON файл"""
        if not self.coordinates:
            messagebox.showwarning("Предупреждение", "Нет координат для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить координаты",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Преобразуем координаты для сохранения (кортежи в списки)
            save_data = {}
            
            for template, template_data in self.coordinates.items():
                save_data[template] = {}
                
                for section, section_data in template_data.items():
                    save_data[template][section] = {}
                    
                    for field, (x, y) in section_data.items():
                        save_data[template][section][field] = [x, y]
            
            # Сохраняем в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Успех", f"Координаты сохранены в {file_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении координат: {e}", exc_info=True)
            messagebox.showerror("Ошибка", f"Не удалось сохранить координаты: {str(e)}")
    
    def load_coordinates(self):
        """Загружает координаты из JSON файла"""
        file_path = filedialog.askopenfilename(
            title="Загрузить координаты",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                load_data = json.load(f)
            
            # Преобразуем загруженные данные (списки в кортежи)
            self.coordinates = {}
            
            for template, template_data in load_data.items():
                self.coordinates[template] = {}
                
                for section, section_data in template_data.items():
                    self.coordinates[template][section] = {}
                    
                    for field, coords in section_data.items():
                        if isinstance(coords, list) and len(coords) == 2:
                            self.coordinates[template][section][field] = (coords[0], coords[1])
            
            # Обновляем список и код
            self.update_coordinates_list()
            self.update_code_output()
            
            messagebox.showinfo("Успех", f"Координаты загружены из {file_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке координат: {e}", exc_info=True)
            messagebox.showerror("Ошибка", f"Не удалось загрузить координаты: {str(e)}")

def main():
    # Проверяем наличие аргументов командной строки
    pdf_path = None
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Файл не найден: {pdf_path}")
            pdf_path = None
    
    # Создаем главное окно
    root = tk.Tk()
    app = PDFCoordinateFinder(root, pdf_path)
    root.mainloop()

if __name__ == "__main__":
    main() 