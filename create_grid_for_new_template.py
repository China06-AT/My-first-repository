#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pymupdf
import os
from datetime import datetime
import subprocess
import platform

def create_grid_for_template(pdf_path, grid_spacing=20, output_dir="output_test"):
    """
    Создает координатную сетку на шаблоне PDF
    
    Args:
        pdf_path: путь к PDF файлу
        grid_spacing: шаг сетки в пикселях
        output_dir: директория для сохранения результата
    
    Returns:
        путь к созданному файлу с сеткой
    """
    print(f"Создание координатной сетки для шаблона: {pdf_path}")
    
    # Проверяем наличие файла
    if not os.path.exists(pdf_path):
        print(f"ОШИБКА: Файл {pdf_path} не найден!")
        return None
    
    # Создаем директорию для выходных файлов если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Открываем PDF и конвертируем в изображение
        pdf_document = pymupdf.open(str(pdf_path))
        page = pdf_document[0]
        zoom = 2.0  # Увеличиваем разрешение в 2 раза
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Конвертируем в PIL Image
        img_data = pix.samples
        img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
        
        # Сохраняем размеры
        width, height = img.width, img.height
        print(f"Размер изображения: {width}x{height}")
        
        # Создаем объект для рисования
        draw = ImageDraw.Draw(img)
        
        # Настройки сетки
        grid_color = (150, 150, 150)  # Серый цвет для линий
        label_color = (50, 50, 50)    # Темно-серый для текста
        
        # Пытаемся загрузить шрифт
        try:
            font_path = "fonts/arial.ttf"
            if not os.path.exists(font_path):
                if platform.system() == "Windows":
                    font_path = "C:/Windows/Fonts/arial.ttf"
                else:
                    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            
            font = ImageFont.truetype(font_path, 14)
        except Exception as e:
            print(f"Невозможно загрузить шрифт: {e}")
            font = ImageFont.load_default()
        
        # Рисуем горизонтальные линии с метками координат
        for y in range(0, height, grid_spacing):
            draw.line((0, y, width, y), fill=grid_color, width=1)
            # Подписываем координаты (учитываем масштаб)
            real_y = int(y/zoom)
            draw.text((5, y+2), f"{real_y}", font=font, fill=label_color)
        
        # Рисуем вертикальные линии с метками координат
        for x in range(0, width, grid_spacing):
            draw.line((x, 0, x, height), fill=grid_color, width=1)
            # Подписываем координаты (учитываем масштаб)
            real_x = int(x/zoom)
            draw.text((x+2, 5), f"{real_x}", font=font, fill=label_color)
        
        # Сохраняем результат с временной меткой
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        template_name = os.path.basename(pdf_path).split('.')[0]
        output_path = os.path.join(output_dir, f"grid_{template_name}_{grid_spacing}_{timestamp}.jpg")
        
        img.save(output_path, quality=95)
        print(f"Координатная сетка сохранена в {output_path}")
        
        # Закрываем PDF
        pdf_document.close()
        
        # Открываем результат в системном просмотрщике
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", output_path])
        else:  # Linux
            subprocess.call(["xdg-open", output_path])
        
        return output_path
    
    except Exception as e:
        print(f"Ошибка при создании сетки: {e}")
        return None

if __name__ == "__main__":
    # Путь к вашему PDF шаблону
    template_path = "Безопастность_и_охрана_труда_корочка_1.pdf"
    
    # Создаем сетку с шагом 20 пикселей
    create_grid_for_template(template_path, grid_spacing=20) 