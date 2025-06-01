#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging
import pymupdf

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_pdf_files(directory='.'):
    """Находит PDF файлы в указанной директории"""
    pdf_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    return pdf_files

def add_grid_to_pdf(pdf_path, output_dir='generated_docs', main_spacing=10, minor_spacing=5, 
                    grid_opacity=120, zoom_factor=2, open_file=True):
    """
    Добавляет координатную сетку на PDF документ
    
    Args:
        pdf_path: Путь к PDF файлу
        output_dir: Директория для сохранения результата
        main_spacing: Шаг основной сетки (в пикселях)
        minor_spacing: Шаг дополнительной сетки (в пикселях)
        grid_opacity: Прозрачность сетки (0-255)
        zoom_factor: Коэффициент масштабирования для лучшего качества
        open_file: Открыть файл после создания
    
    Returns:
        str: Путь к созданному файлу
    """
    try:
        # Создаем директорию для результатов, если она не существует
        os.makedirs(output_dir, exist_ok=True)
        
        # Открываем PDF
        logger.info(f"Открываю PDF файл: {pdf_path}")
        pdf_document = pymupdf.open(pdf_path)
        
        # Берем первую страницу
        page = pdf_document[0]
        
        # Преобразуем в изображение с улучшенным качеством
        mat = pymupdf.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=mat)
        
        # Сохраняем во временный файл
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = os.path.join(output_dir, f"temp_{timestamp}.png")
        pix.save(temp_path)
        
        # Открываем изображение с помощью PIL
        img = Image.open(temp_path)
        width, height = img.width, img.height
        logger.info(f"Размер изображения: {width}x{height} пикселей")
        
        # Находим системный шрифт
        system_font = os.path.join('C:/Windows/Fonts', 'arial.ttf')
        if not os.path.exists(system_font):
            logger.warning("Системный шрифт не найден, используем стандартный")
            label_font = ImageFont.load_default()
            big_label_font = ImageFont.load_default()
        else:
            try:
                label_font = ImageFont.truetype(system_font, 10)
                big_label_font = ImageFont.truetype(system_font, 14)
            except Exception as e:
                logger.error(f"Ошибка загрузки шрифта: {e}")
                label_font = ImageFont.load_default()
                big_label_font = ImageFont.load_default()
        
        # Создаем полупрозрачный слой для сетки
        grid_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(grid_layer)
        
        # Цвета для сетки
        minor_color = (200, 200, 200, grid_opacity // 2)  # Светло-серый для дополнительных линий
        main_color = (100, 100, 100, grid_opacity)        # Темно-серый для основных линий
        label_bg = (255, 255, 255, 180)                   # Фон для подписей
        
        # Рисуем дополнительные линии (более тонкие)
        if minor_spacing > 0:
            for y in range(0, height, minor_spacing):
                if y % main_spacing != 0:  # Не основная линия
                    draw.line((0, y, width, y), fill=minor_color, width=1)
            
            for x in range(0, width, minor_spacing):
                if x % main_spacing != 0:  # Не основная линия
                    draw.line((x, 0, x, height), fill=minor_color, width=1)
        
        # Рисуем основные линии
        for y in range(0, height, main_spacing):
            # Горизонтальная линия
            draw.line((0, y, width, y), fill=main_color, width=1)
            # Подписываем координату Y (оригинальные координаты)
            real_y = int(y/zoom_factor)
            draw.rectangle((2, y-7, 30, y+7), fill=label_bg)
            draw.text((4, y-6), f"{real_y}", font=label_font, fill=(0, 0, 0))
        
        for x in range(0, width, main_spacing):
            # Вертикальная линия
            draw.line((x, 0, x, height), fill=main_color, width=1)
            # Подписываем координату X (оригинальные координаты)
            real_x = int(x/zoom_factor)
            draw.rectangle((x-15, 2, x+15, 16), fill=label_bg)
            draw.text((x-14 if real_x >= 100 else x-10, 3), f"{real_x}", font=label_font, fill=(0, 0, 0))
        
        # Добавляем метки каждые 50 пикселей для лучшей навигации
        for y in range(0, height, 50):
            real_y = int(y/zoom_factor)
            draw.rectangle((2, y-9, 40, y+9), fill=(240, 240, 255, 200))
            draw.text((4, y-7), f"{real_y}", font=big_label_font, fill=(0, 0, 150))
        
        for x in range(0, width, 50):
            real_x = int(x/zoom_factor)
            draw.rectangle((x-20, 2, x+20, 20), fill=(240, 240, 255, 200))
            draw.text((x-15, 3), f"{real_x}", font=big_label_font, fill=(0, 0, 150))
        
        # Добавляем заголовок с информацией
        title = f"Координатная сетка (шаг {int(main_spacing/zoom_factor)}px, доп. линии {int(minor_spacing/zoom_factor)}px)"
        draw.rectangle((width//2-200, 2, width//2+200, 25), fill=(240, 240, 255, 230))
        draw.text((width//2-190, 5), title, font=big_label_font, fill=(0, 0, 150))
        
        # Накладываем сетку на изображение
        result_img = Image.alpha_composite(img.convert('RGBA'), grid_layer).convert('RGB')
        
        # Формируем имя выходного файла
        pdf_name = os.path.basename(pdf_path).split('.')[0]
        output_path = os.path.join(output_dir, f"{pdf_name}_grid_{int(main_spacing/zoom_factor)}px_{timestamp}.jpg")
        
        # Сохраняем результат
        result_img.save(output_path, quality=95)
        logger.info(f"Сетка наложена и сохранена в: {output_path}")
        
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Открываем изображение, если требуется
        if open_file:
            try:
                logger.info("Открываю файл для просмотра...")
                if os.name == 'nt':  # Windows
                    os.startfile(output_path)
                else:
                    import subprocess
                    if os.name == 'posix':  # macOS или Linux
                        opener = 'open' if os.uname().sysname == 'Darwin' else 'xdg-open'
                        subprocess.call([opener, output_path])
            except Exception as e:
                logger.error(f"Ошибка при открытии файла: {e}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Ошибка наложения сетки на PDF: {e}")
        return None

def main():
    try:
        # Создаем директорию для результатов
        output_dir = 'generated_docs'
        os.makedirs(output_dir, exist_ok=True)
        
        # Параметры сетки
        main_spacing = 20   # Шаг основной сетки (в пикселях оригинального изображения)
        minor_spacing = 5   # Шаг дополнительной сетки (в пикселях оригинального изображения)
        grid_opacity = 120  # Прозрачность сетки (0-255)
        zoom_factor = 2     # Коэффициент масштабирования для лучшего качества
        
        # Находим PDF файлы
        pdf_files = find_pdf_files()
        
        if not pdf_files:
            print("❌ Ошибка: PDF файлы не найдены в текущей директории")
            return
        
        # Выводим список найденных файлов
        print("Найдены следующие PDF файлы:")
        for i, file in enumerate(pdf_files, 1):
            print(f"{i}. {os.path.basename(file)}")
            
        # Спрашиваем пользователя, какой файл использовать
        if len(pdf_files) > 1:
            choice = input("Введите номер файла для нанесения сетки (или Enter для первого): ")
            try:
                idx = int(choice) - 1 if choice.strip() else 0
                if idx < 0 or idx >= len(pdf_files):
                    idx = 0
            except ValueError:
                idx = a
        else:
            idx = 0
        
        selected_pdf = pdf_files[idx]
        print(f"Выбран файл: {os.path.basename(selected_pdf)}")
        
        # Накладываем сетку
        output_path = add_grid_to_pdf(
            pdf_path=selected_pdf,
            output_dir=output_dir,
            main_spacing=main_spacing * zoom_factor,  # Умножаем на zoom_factor для масштабированного изображения
            minor_spacing=minor_spacing * zoom_factor,
            grid_opacity=grid_opacity,
            zoom_factor=zoom_factor
        )
        
        if output_path:
            print(f"✅ Готово! Сетка наложена на документ и сохранена: {output_path}")
        else:
            print("❌ Ошибка при наложении сетки на документ")
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 