#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import pymupdf
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import platform
import subprocess
from datetime import datetime

def analyze_pdf_areas(pdf_path, output_dir="generated_docs"):
    """
    Анализирует PDF и определяет области для размещения текста
    
    Args:
        pdf_path: Путь к PDF файлу
        output_dir: Директория для сохранения результатов
    
    Returns:
        Словарь с координатами для разных полей
    """
    print(f"Анализ PDF шаблона: {pdf_path}")
    
    # Проверка существования файла
    if not os.path.exists(pdf_path):
        print(f"ОШИБКА: Файл {pdf_path} не найден!")
        return None
    
    # Создаем выходную директорию
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Открываем PDF и преобразуем его в изображение
        pdf_document = pymupdf.open(str(pdf_path))
        page = pdf_document[0]
        zoom = 2.0  # Увеличиваем разрешение
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Сохраняем временно как PNG
        temp_png = os.path.join(output_dir, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pix.save(temp_png)
        
        # Размеры изображения
        width, height = pix.width, pix.height
        print(f"Размер изображения: {width}x{height} пикселей")
        
        # Преобразуем в numpy array для анализа
        img = Image.open(temp_png)
        img_array = np.array(img)
        
        # Определяем имя шаблона для использования в координатах
        template_name = os.path.basename(pdf_path).split('.')[0].upper().replace(' ', '_').replace('-', '_')
        
        # Создаем структуру для хранения координат
        coordinates = {
            template_name: {
                'LEFT': {},
                'RIGHT': {}
            }
        }
        
        # Координаты для БиОТ - их нужно определить на основе анализа
        # Используем эвристики для определения областей
        
        # ----- ЛЕВАЯ СТОРОНА -----
        # Установка координат с учетом обычного расположения полей
        left_side_mid_x = int(width * 0.3 / zoom)  # Примерно 30% от ширины
        
        # Номер удостоверения (обычно в верхней части)
        coordinates[template_name]['LEFT']['protocol_number'] = (int(width * 0.4 / zoom), int(height * 0.25 / zoom))
        
        # Организация (ниже номера удостоверения)
        coordinates[template_name]['LEFT']['workplace'] = (left_side_mid_x, int(height * 0.32 / zoom))
        
        # ФИО (ниже организации)
        coordinates[template_name]['LEFT']['fullname'] = (left_side_mid_x, int(height * 0.39 / zoom))
        
        # Должность (ниже ФИО)
        coordinates[template_name]['LEFT']['job_title'] = (left_side_mid_x, int(height * 0.46 / zoom))
        
        # Даты выдачи (внизу левой стороны)
        date_y = int(height * 0.6 / zoom)
        coordinates[template_name]['LEFT']['cert_day'] = (int(width * 0.25 / zoom), date_y)
        coordinates[template_name]['LEFT']['cert_month'] = (int(width * 0.28 / zoom), date_y)
        coordinates[template_name]['LEFT']['cert_year'] = (int(width * 0.33 / zoom), date_y)
        
        # ----- ПРАВАЯ СТОРОНА (таблица) -----
        right_side_x = int(width * 0.6 / zoom)
        row_y = int(height * 0.5 / zoom)
        
        # Распределяем позиции в "таблице" равномерно
        table_x_positions = [
            int(width * 0.6 / zoom),   # Дата проверки
            int(width * 0.7 / zoom),   # Причина
            int(width * 0.8 / zoom),   # Оценка
            int(width * 0.9 / zoom)    # Следующая дата
        ]
        
        coordinates[template_name]['RIGHT']['cert_date'] = (table_x_positions[0], row_y)
        coordinates[template_name]['RIGHT']['reason'] = (table_x_positions[1], row_y)
        coordinates[template_name]['RIGHT']['mark'] = (table_x_positions[2], row_y)
        coordinates[template_name]['RIGHT']['next_date'] = (table_x_positions[3], row_y)
        
        # Создаем визуальное представление обнаруженных координат
        img_draw = ImageDraw.Draw(img)
        
        # Загружаем шрифт
        try:
            font_path = "fonts/arial.ttf"
            if not os.path.exists(font_path):
                if platform.system() == "Windows":
                    font_path = "C:/Windows/Fonts/arial.ttf"
                elif platform.system() == "Darwin":  # macOS
                    font_path = "/Library/Fonts/Arial.ttf"
                else:  # Linux
                    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            
            font_normal = ImageFont.truetype(font_path, 20)
            font_small = ImageFont.truetype(font_path, 12)
        except Exception as e:
            print(f"Не удалось загрузить шрифт: {e}")
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Добавляем круги и подписи на изображение для каждой координаты
        for section, fields in coordinates[template_name].items():
            for field, (x, y) in fields.items():
                scaled_x = int(x * zoom)
                scaled_y = int(y * zoom)
                
                # Рисуем желтый круг
                circle_radius = 8
                img_draw.ellipse(
                    [(scaled_x - circle_radius, scaled_y - circle_radius),
                     (scaled_x + circle_radius, scaled_y + circle_radius)],
                    outline=(255, 0, 0),
                    fill=(255, 255, 0)
                )
                
                # Добавляем подпись
                img_draw.text(
                    (scaled_x + circle_radius + 5, scaled_y - 10),
                    f"{field} ({x}, {y})",
                    fill=(255, 0, 0),
                    font=font_small
                )
        
        # Добавляем заголовок
        img_draw.text(
            (50, 50),
            f"Автоматически определенные координаты для {template_name}",
            fill=(0, 0, 255),
            font=font_normal
        )
        
        # Сохраняем изображение с координатами
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        coords_img_path = os.path.join(output_dir, f"auto_coords_{template_name}_{timestamp}.jpg")
        img.save(coords_img_path, quality=95)
        
        print(f"Визуализация координат сохранена: {coords_img_path}")
        
        # Сохраняем координаты в JSON
        json_path = os.path.join(output_dir, f"auto_coords_{template_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(coordinates, f, ensure_ascii=False, indent=4)
        
        print(f"Координаты сохранены в JSON: {json_path}")
        
        # Удаляем временный файл
        if os.path.exists(temp_png):
            os.remove(temp_png)
        
        # Открываем изображение с координатами
        try:
            if platform.system() == "Windows":
                os.startfile(coords_img_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", coords_img_path])
            else:  # Linux
                subprocess.call(["xdg-open", coords_img_path])
        except Exception as e:
            print(f"Не удалось открыть файл: {e}")
        
        # Скрипт для интеграции координат в генератор
        create_integration_script(coordinates)
        
        return coordinates
    
    except Exception as e:
        print(f"Ошибка при анализе PDF: {e}")
        return None

def create_integration_script(coordinates):
    """Создает файл скрипта для интеграции координат"""
    # Создаем содержимое скрипта
    content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from image_certificate_generator import ImageCertificateGenerator

def apply_auto_coordinates():
    \"\"\"
    Применяет автоматически определенные координаты к image_certificate_generator.py
    и исправляет обработку имени шаблона
    \"\"\"
    # Загружаем автоматически определенные координаты
    coordinates = """
    
    # Добавляем координаты в виде кода Python
    content += json.dumps(coordinates, ensure_ascii=False, indent=4)
    
    # Добавляем остальную часть скрипта
    content += """
    
    # Исправляем файл image_certificate_generator.py
    generator_file = "image_certificate_generator.py"
    
    if not os.path.exists(generator_file):
        print(f"ОШИБКА: Файл {generator_file} не найден!")
        return False
    
    try:
        # Создаем резервную копию
        backup_file = f"{generator_file}.auto_backup"
        import shutil
        shutil.copy2(generator_file, backup_file)
        print(f"Создана резервная копия файла: {backup_file}")
        
        # Считываем содержимое файла
        with open(generator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем метод _fill_ohrana_truda для динамического определения шаблона
        old_method = re.search(r'def _fill_ohrana_truda\(self, draw, data, scale_factor\):.*?""".*?"""(.*?)def', content, re.DOTALL)
        
        if old_method:
            old_code = old_method.group(1)
            
            # Создаем новую версию метода
            new_code = old_code.replace(
                "coords = self.COORDINATES['OHRANA_TRUDA']['LEFT']", 
                "# Динамически определяем шаблон из переданного пути к файлу или используем OHRANA_TRUDA\\n        "
                "template_name = data.get('template_name', 'OHRANA_TRUDA')\\n        "
                "if template_name in self.COORDINATES:\\n            "
                "coords = self.COORDINATES[template_name]['LEFT']\\n        "
                "else:\\n            "
                "coords = self.COORDINATES['OHRANA_TRUDA']['LEFT']"
            )
            
            # Аналогично заменяем для правой части
            new_code = new_code.replace(
                "right_coords = self.COORDINATES['OHRANA_TRUDA']['RIGHT']", 
                "right_coords = self.COORDINATES[template_name]['RIGHT'] if template_name in self.COORDINATES else self.COORDINATES['OHRANA_TRUDA']['RIGHT']"
            )
            
            # Заменяем в файле
            content = content.replace(old_code, new_code)
            
            # Обновляем метод _create_electrobez_korotchka для передачи имени шаблона
            create_method = re.search(r'def _create_electrobez_korotchka\(self, template_path, data, output_filename, debug_mode=False, grid_density=20\):.*?""".*?"""(.*?)try:', content, re.DOTALL)
            
            if create_method:
                old_create_code = create_method.group(1)
                new_create_code = old_create_code.replace(
                    "# Проверка файла шаблона", 
                    "# Получаем имя шаблона из пути к файлу\\n        "
                    "template_name = os.path.basename(template_path).split('.')[0].upper().replace(' ', '_').replace('-', '_')\\n        "
                    "data['template_name'] = template_name\\n        "
                    "print(f\"Используется шаблон: {template_name}\")\\n        "
                    "# Проверка файла шаблона"
                )
                
                content = content.replace(old_create_code, new_create_code)
            
            # Найдем блок COORDINATES и заменим его
            coords_block = re.search(r'    COORDINATES = \{.*?\n    \}', content, re.DOTALL)
            if coords_block:
                new_coords_block = "    COORDINATES = {\n"
                
                # Добавляем существующие координаты LEFT и RIGHT
                new_coords_block += "        # Левая часть для электробезопасности\n"
                new_coords_block += "        'LEFT': {\n"
                new_coords_block += "            'protocol_number': (257, 75),  # Номер удостоверения\n"
                new_coords_block += "            'workplace': (260, 115),       # Организация \n"
                new_coords_block += "            'fullname': (260, 155),        # ФИО\n"
                new_coords_block += "            'job_title': (260, 225),       # Должность\n"
                new_coords_block += "            'group_text': (190, 300),      # Группа допуска\n"
                new_coords_block += "            'cert_day': (273, 345),        # День выдачи\n"
                new_coords_block += "            'cert_month': (295, 345),      # Месяц выдачи\n"
                new_coords_block += "            'cert_year': (339, 345)        # Год выдачи\n"
                new_coords_block += "        },\n"
                
                new_coords_block += "        # Правая часть (таблица) для электробезопасности\n"
                new_coords_block += "        'RIGHT': {\n"
                new_coords_block += "            'cert_date': (868, 155),      # Дата проверки\n"
                new_coords_block += "            'reason': (949, 155),         # Причина проверки\n"
                new_coords_block += "            'group': (1065, 155),         # Группа (римская)\n"
                new_coords_block += "            'mark': (1156, 155),          # Оценка\n"
                new_coords_block += "            'next_date': (1246, 155)      # Дата следующей проверки\n"
                new_coords_block += "        },\n"
                
                new_coords_block += "        # Координаты для Безопасности и Охраны труда\n"
                new_coords_block += "        'OHRANA_TRUDA': {\n"
                new_coords_block += "            'LEFT': {\n"
                new_coords_block += "                'protocol_number': (440, 440),  # Номер удостоверения\n"
                new_coords_block += "                'workplace': (320, 280),       # Организация \n"
                new_coords_block += "                'fullname': (260, 155),        # ФИО\n"
                new_coords_block += "                'job_title': (320,100),       # Должность\n"
                new_coords_block += "                'cert_day': (273, 345),        # День выдачи\n"
                new_coords_block += "                'cert_month': (295, 345),      # Месяц выдачи\n"
                new_coords_block += "                'cert_year': (339, 345)        # Год выдачи\n"
                new_coords_block += "            },\n"
                new_coords_block += "            'RIGHT': {\n"
                new_coords_block += "                'cert_date': (868, 155),      # Дата проверки\n"
                new_coords_block += "                'reason': (949, 155),         # Причина проверки\n"
                new_coords_block += "                'mark': (1156, 155),          # Оценка\n"
                new_coords_block += "                'next_date': (1246, 155)      # Дата следующей проверки\n"
                new_coords_block += "            }\n"
                new_coords_block += "        },\n"
                
                # Добавляем автоматически определенные координаты
                for template_name, template_data in coordinates.items():
                    new_coords_block += f"        # Автоматически определенные координаты для {template_name}\n"
                    new_coords_block += f"        '{template_name}': {{\n"
                    
                    for section, section_data in template_data.items():
                        new_coords_block += f"            '{section}': {{\n"
                        
                        for field, coords in section_data.items():
                            new_coords_block += f"                '{field}': {coords},  # Автоопределено\n"
                        
                        if section == list(template_data.keys())[-1]:
                            new_coords_block += "            }\n"
                        else:
                            new_coords_block += "            },\n"
                    
                    if template_name == list(coordinates.keys())[-1]:
                        new_coords_block += "        }\n"
                    else:
                        new_coords_block += "        },\n"
                
                new_coords_block += "    }"
                
                # Заменяем блок координат
                content = content.replace(coords_block.group(0), new_coords_block)
            
            # Записываем в файл
            with open(generator_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Координаты и исправления успешно применены!")
            return True
            
        else:
            print("❌ Не удалось найти метод _fill_ohrana_truda.")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при применении координат: {e}")
        return False

if __name__ == "__main__":
    apply_auto_coordinates()
"""
    
    script_path = "apply_auto_coordinates.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Создаем батник
    batch_content = """@echo off
echo Применение автоматически определенных координат...
python apply_auto_coordinates.py
pause
"""
    
    batch_path = "apply_auto_coordinates.bat"
    with open(batch_path, "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print(f"Созданы файлы для интеграции координат:")
    print(f" - {script_path}")
    print(f" - {batch_path}")

if __name__ == "__main__":
    print("=" * 70)
    print(" АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ КООРДИНАТ ДЛЯ PDF ШАБЛОНА ")
    print("=" * 70)
    
    # Запрашиваем путь к PDF файлу
    pdf_path = input("Введите путь к PDF шаблону [Безопастность_и_охрана_труда_корочка_1.pdf]: ").strip()
    if not pdf_path:
        pdf_path = "Безопастность_и_охрана_труда_корочка_1.pdf"
    
    # Анализируем PDF
    coordinates = analyze_pdf_areas(pdf_path)
    
    if coordinates:
        print("\nКоординаты были определены автоматически.")
        print("Для применения координат запустите:")
        print("   apply_auto_coordinates.bat")
        print("\nПосле применения координат можно протестировать результат:")
        print("   python test_coordinates.py")
    else:
        print("\nНе удалось определить координаты.")
    
    print("=" * 70) 