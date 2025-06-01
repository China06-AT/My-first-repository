#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from PIL import Image, ImageDraw, ImageFont
import pymupdf
from datetime import datetime

def auto_find_coordinates(pdf_path, output_dir="output_test"):
    """
    Создаем координатную сетку и автоматически распознаем места для заполнения в шаблоне
    
    Args:
        pdf_path: путь к PDF файлу
        output_dir: директория для сохранения результата
    """
    print(f"Обрабатываем шаблон: {pdf_path}")
    
    # Проверяем наличие файла
    if not os.path.exists(pdf_path):
        print(f"ОШИБКА: Файл {pdf_path} не найден!")
        return
    
    # Создаем директорию для выходных файлов если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Получаем имя шаблона из имени файла
        template_name = os.path.basename(pdf_path).split('.')[0].upper().replace(' ', '_')
        print(f"Имя шаблона: {template_name}")
        
        # Открываем PDF и конвертируем в изображение
        pdf_document = pymupdf.open(str(pdf_path))
        page = pdf_document[0]
        zoom = 2.0  # Увеличиваем разрешение в 2 раза
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Сохраняем изображение во временный файл
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_img_path = os.path.join(output_dir, f"temp_{template_name}_{timestamp}.png")
        pix.save(temp_img_path)
        
        # Предварительные координаты для охраны труда
        # Это примерные координаты, которые можно будет настроить
        coordinates = {
            template_name: {
                'LEFT': {
                    'protocol_number': (290, 303),  # Номер удостоверения
                    'workplace': (173, 340),        # Организация 
                    'fullname': (173, 373),         # ФИО
                    'job_title': (173, 406),        # Должность
                    'cert_day': (254, 530),         # День выдачи
                    'cert_month': (283, 530),       # Месяц выдачи
                    'cert_year': (375, 530)         # Год выдачи
                },
                'RIGHT': {
                    'cert_date': (733, 377),       # Дата проверки
                    'reason': (803, 377),          # Причина проверки
                    'mark': (947, 377),            # Оценка
                    'next_date': (1085, 377)       # Дата следующей проверки
                }
            }
        }
        
        # Создаем изображение с отметками координат
        img = Image.open(temp_img_path)
        draw = ImageDraw.Draw(img)
        
        # Пытаемся загрузить шрифт
        try:
            font_path = "C:/Windows/Fonts/arial.ttf"
            font = ImageFont.truetype(font_path, 20)
        except Exception as e:
            print(f"Невозможно загрузить шрифт: {e}")
            font = ImageFont.load_default()
        
        # Размер точки для отображения координат
        dot_radius = 5
        
        # Отмечаем все координаты на изображении
        for section, fields in coordinates[template_name].items():
            for field, (x, y) in fields.items():
                # Умножаем на масштаб для точности
                scaled_x = int(x * zoom)
                scaled_y = int(y * zoom)
                
                # Рисуем круг на координатах
                draw.ellipse(
                    [(scaled_x - dot_radius, scaled_y - dot_radius), 
                     (scaled_x + dot_radius, scaled_y + dot_radius)], 
                    fill=(255, 0, 0)  # Красный цвет
                )
                
                # Добавляем подпись
                draw.text(
                    (scaled_x + 10, scaled_y - 10), 
                    f"{field} ({x}, {y})", 
                    fill=(255, 0, 0), 
                    font=font
                )
        
        # Сохраняем изображение с отметками
        marked_img_path = os.path.join(output_dir, f"coordinates_{template_name}_{timestamp}.png")
        img.save(marked_img_path)
        print(f"Изображение с отмеченными координатами сохранено: {marked_img_path}")
        
        # Сохраняем координаты в JSON
        json_path = os.path.join(output_dir, f"coordinates_{template_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(coordinates, f, ensure_ascii=False, indent=4)
        print(f"Координаты сохранены в файл: {json_path}")
        
        # Очищаем временные файлы
        pdf_document.close()
        
        # Открываем созданное изображение
        try:
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                os.startfile(marked_img_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", marked_img_path])
            else:  # Linux
                subprocess.call(["xdg-open", marked_img_path])
        except Exception as e:
            print(f"Не удалось открыть файл с изображением: {e}")
        
        return json_path
    
    except Exception as e:
        print(f"Ошибка при обработке PDF: {e}")
        return None

if __name__ == "__main__":
    # Путь к новому шаблону
    template_path = "Безопастность_и_охрана_труда_корочка_1.pdf"
    
    # Запускаем поиск координат
    auto_find_coordinates(template_path) 