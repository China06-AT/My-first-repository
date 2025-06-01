#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pymupdf
import platform
import subprocess

def test_coordinates(pdf_path, coordinates_json=None, custom_coordinates=None):
    """
    Создает тестовое изображение с текстом, размещенным по указанным координатам
    
    Args:
        pdf_path: Путь к PDF шаблону
        coordinates_json: Путь к JSON-файлу с координатами (опционально)
        custom_coordinates: Словарь с координатами (опционально)
    
    Returns:
        Путь к созданному тестовому файлу
    """
    print(f"Тестирование координат для шаблона: {pdf_path}")
    
    # Проверяем наличие шаблона
    if not os.path.exists(pdf_path):
        print(f"ОШИБКА: Шаблон {pdf_path} не найден!")
        return None
    
    # Получаем координаты из файла или используем переданные
    coordinates = {}
    if coordinates_json and os.path.exists(coordinates_json):
        try:
            with open(coordinates_json, 'r', encoding='utf-8') as f:
                coordinates = json.load(f)
            print(f"Координаты загружены из {coordinates_json}")
        except Exception as e:
            print(f"Ошибка при загрузке координат из JSON: {e}")
    elif custom_coordinates:
        coordinates = custom_coordinates
        print("Используются переданные координаты")
    else:
        print("ВНИМАНИЕ: Координаты не указаны. Пустой тест!")
    
    # Конвертируем PDF в изображение
    try:
        pdf_document = pymupdf.open(str(pdf_path))
        page = pdf_document[0]
        zoom = 2.0  # Высокое разрешение для точности
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Сохраняем во временный файл
        output_dir = "generated_docs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        temp_png = os.path.join(output_dir, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pix.save(temp_png)
        
        # Открываем сохраненное изображение
        img = Image.open(temp_png)
        draw = ImageDraw.Draw(img)
        
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
        
        # Размещаем текст по координатам из JSON файла с учетом масштаба
        for template_name, template_coords in coordinates.items():
            # Выводим название шаблона крупным текстом сверху
            watermark_text = f"ТЕСТ КООРДИНАТ - {template_name}"
            draw.text((100, 50), watermark_text, fill=(255, 0, 0), font=font_normal)
            
            for section_name, section_coords in template_coords.items():
                for field_name, coords in section_coords.items():
                    x, y = coords
                    # Учитываем масштаб PDF
                    scaled_x = int(x * zoom)
                    scaled_y = int(y * zoom)
                    
                    # Генерируем тестовый текст для каждого поля
                    text_examples = {
                        'protocol_number': '123-456',
                        'workplace': 'ТОО "Тест"',
                        'fullname': 'Иванов И.И.',
                        'job_title': 'Инженер',
                        'group_text': 'Группа III',
                        'cert_day': '01',
                        'cert_month': '06',
                        'cert_year': '24',
                        'cert_date': '01.06.2024',
                        'reason': 'Первичная',
                        'group': 'III',
                        'mark': 'Отлично',
                        'next_date': '01.06.2025'
                    }
                    
                    text_to_draw = text_examples.get(field_name, field_name)
                    
                    # Добавляем круг на координатах
                    circle_radius = 5
                    draw.ellipse(
                        [(scaled_x - circle_radius, scaled_y - circle_radius),
                         (scaled_x + circle_radius, scaled_y + circle_radius)],
                        outline=(255, 0, 0), fill=(255, 255, 0)
                    )
                    
                    # Рисуем текст
                    draw.text(
                        (scaled_x, scaled_y), 
                        text_to_draw, 
                        fill=(0, 0, 255), 
                        font=font_normal
                    )
                    
                    # Добавляем подпись с именем поля и координатами
                    label = f"{field_name} ({x}, {y})"
                    label_offset_y = 25
                    draw.text(
                        (scaled_x, scaled_y + label_offset_y), 
                        label, 
                        fill=(255, 0, 0), 
                        font=font_small
                    )
        
        # Сохраняем результат
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        template_name = os.path.basename(pdf_path).split('.')[0]
        output_path = os.path.join(output_dir, f"test_coordinates_{template_name}_{timestamp}.jpg")
        img.save(output_path, quality=95)
        
        print(f"Изображение с тестовыми координатами сохранено: {output_path}")
        
        # Удаляем временный файл
        if os.path.exists(temp_png):
            os.remove(temp_png)
        
        # Открываем созданный файл
        try:
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", output_path])
            else:  # Linux
                subprocess.call(["xdg-open", output_path])
        except Exception as e:
            print(f"Не удалось открыть файл: {e}")
        
        return output_path
    
    except Exception as e:
        print(f"Ошибка при тестировании координат: {e}")
        return None

def debug_all_coordinates(pdf_path, json_file=None):
    """
    Функция для отладки всех координат из image_certificate_generator.py
    или переданного JSON файла
    """
    # Проверяем наличие JSON файла
    if json_file and os.path.exists(json_file):
        # Используем координаты из JSON файла
        return test_coordinates(pdf_path, coordinates_json=json_file)
    else:
        # Используем жестко заданные координаты для тестирования
        test_coords = {
            'БЕЗОПАСТНОСТЬ_И_ОХРАНА_ТРУДА_КОРОЧКА_1': {
                'LEFT': {
                    'protocol_number': (440, 200),  # Номер удостоверения
                    'workplace': (320, 240),        # Организация 
                    'fullname': (320, 280),         # ФИО
                    'job_title': (320, 320),        # Должность
                    'cert_day': (273, 400),         # День выдачи
                    'cert_month': (295, 400),       # Месяц выдачи
                    'cert_year': (339, 400)         # Год выдачи
                },
                'RIGHT': {
                    'cert_date': (733, 500),       # Дата проверки
                    'reason': (803, 500),          # Причина проверки
                    'mark': (947, 500),            # Оценка
                    'next_date': (1085, 500)       # Дата следующей проверки
                }
            }
        }
        
        # Запускаем тест с особыми тестовыми координатами
        return test_coordinates(pdf_path, custom_coordinates=test_coords)

if __name__ == "__main__":
    print("Тестирование координат на PDF шаблоне")
    print("=" * 60)
    
    # Запрашиваем путь к файлу шаблона
    template_file = input("Введите путь к PDF шаблону [Безопастность_и_охрана_труда_корочка_1.pdf]: ").strip()
    if not template_file:
        template_file = "Безопастность_и_охрана_труда_корочка_1.pdf"
    
    # Спрашиваем, использовать ли JSON файл с координатами
    use_json = input("Использовать JSON файл с координатами? (y/n) [y]: ").strip().lower()
    if use_json != 'n':
        json_file = input("Введите путь к JSON файлу [coordinates.json]: ").strip()
        if not json_file:
            json_file = "coordinates.json"
        
        debug_all_coordinates(template_file, json_file)
    else:
        debug_all_coordinates(template_file)
    
    print("\nПроверьте созданное изображение в папке generated_docs")
    print("На нем должны быть видны желтые кружки с текстом в местах, соответствующих координатам") 