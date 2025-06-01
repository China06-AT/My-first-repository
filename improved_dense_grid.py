#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_enhanced_grid(width=1684, height=1190, main_spacing=20, minor_spacing=5, 
                        grid_opacity=80, font_path=None):
    """
    Создает улучшенную координатную сетку с основными и дополнительными линиями
    
    Args:
        width: Ширина сетки
        height: Высота сетки
        main_spacing: Расстояние между основными линиями
        minor_spacing: Расстояние между дополнительными линиями
        grid_opacity: Прозрачность сетки (0-255)
        font_path: Путь к шрифту
    
    Returns:
        Image: Объект изображения с сеткой
    """
    # Создаем белый фон
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Находим подходящий шрифт
    if not font_path:
        system_font = os.path.join('C:/Windows/Fonts', 'arial.ttf')
        if os.path.exists(system_font):
            font_path = system_font
        else:
            logger.warning("Системный шрифт не найден, используем стандартный")
    
    try:
        label_font = ImageFont.truetype(font_path, 10) if font_path else ImageFont.load_default()
        big_label_font = ImageFont.truetype(font_path, 14) if font_path else ImageFont.load_default()
    except Exception as e:
        logger.error(f"Ошибка загрузки шрифта: {e}")
        label_font = ImageFont.load_default()
        big_label_font = ImageFont.load_default()
    
    # Цвета для сетки
    minor_color = (200, 200, 200, grid_opacity)  # Светло-серый для дополнительных линий
    main_color = (100, 100, 100, grid_opacity + 50)  # Темно-серый для основных линий
    axis_color = (50, 50, 200, grid_opacity + 70)  # Синий для осей координат
    
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
        # Рисуем линию немного толще
        draw.line((0, y, width, y), fill=main_color, width=1)
        # Подписываем координату Y
        draw.rectangle((5, y-8, 35, y+8), fill=(255, 255, 255, 200))
        draw.text((8, y-6), f"{y}", font=label_font, fill=(0, 0, 0))
    
    for x in range(0, width, main_spacing):
        # Рисуем линию немного толще
        draw.line((x, 0, x, height), fill=main_color, width=1)
        # Подписываем координату X
        draw.rectangle((x-15, 5, x+15, 18), fill=(255, 255, 255, 200))
        draw.text((x-8, 6), f"{x}", font=label_font, fill=(0, 0, 0))
    
    # Добавляем метки каждые 100 пикселей для лучшей навигации
    for y in range(0, height, 100):
        draw.rectangle((5, y-10, 50, y+10), fill=(240, 240, 255, 230))
        draw.text((8, y-7), f"{y}", font=big_label_font, fill=(0, 0, 150))
    
    for x in range(0, width, 100):
        draw.rectangle((x-20, 5, x+20, 25), fill=(240, 240, 255, 230))
        draw.text((x-15, 7), f"{x}", font=big_label_font, fill=(0, 0, 150))
    
    # Добавляем заголовок с информацией
    title = f"Координатная сетка {width}x{height} (шаг {main_spacing}px, доп. линии {minor_spacing}px)"
    draw.rectangle((width//2-300, 5, width//2+300, 30), fill=(240, 240, 255, 230))
    draw.text((width//2-290, 8), title, font=big_label_font, fill=(0, 0, 150))
    
    return img

def main():
    try:
        # Параметры сетки
        width = 1684        # Стандартная ширина шаблона корочки
        height = 1190       # Стандартная высота шаблона корочки
        main_spacing = 20   # Шаг основной сетки (в пикселях)
        minor_spacing = 5   # Шаг дополнительной сетки (в пикселях)
        grid_opacity = 90   # Прозрачность сетки (0-255)
        
        # Создаем директорию для результатов, если она не существует
        output_dir = 'generated_docs'
        os.makedirs(output_dir, exist_ok=True)
        
        # Создаем сетку
        logger.info(f"Создаем улучшенную координатную сетку {width}x{height} с шагом {main_spacing}/{minor_spacing}px")
        img = create_enhanced_grid(
            width=width, 
            height=height, 
            main_spacing=main_spacing, 
            minor_spacing=minor_spacing,
            grid_opacity=grid_opacity
        )
        
        # Сохраняем изображение
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f"enhanced_grid_{main_spacing}px_{timestamp}.jpg")
        img.save(output_path, quality=95)
        logger.info(f"Сетка сохранена в {output_path}")
        
        # Открываем изображение
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
        
        print(f"✅ Готово! Улучшенная координатная сетка успешно создана и сохранена: {output_path}")
        
    except Exception as e:
        logger.error(f"Ошибка создания сетки: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 