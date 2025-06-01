from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from datetime import datetime

def create_readable_ruler(width=1700, height=150, output_dir='generated_docs'):
    """
    Создает читабельную горизонтальную линейку с четкими цифрами.
    
    Args:
        width: Ширина линейки в пикселях
        height: Высота линейки в пикселях
        output_dir: Директория для сохранения результата
    
    Returns:
        str: Путь к сохраненному файлу
    """
    # Создаем белый холст
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать Arial для Windows или системный шрифт
    try:
        system_font = Path('C:/Windows/Fonts/arial.ttf')
        if system_font.exists():
            font_path = system_font
        else:
            if not os.path.exists('fonts'):
                os.makedirs('fonts')
            font_path = Path('fonts/arial.ttf')
        
        # Используем достаточно большой шрифт для цифр
        big_font = ImageFont.truetype(str(font_path), 14)
        small_font = ImageFont.truetype(str(font_path), 10)
    except Exception:
        # Если не получилось загрузить шрифт, используем стандартный
        big_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Настройки линейки
    main_color = (0, 0, 0)         # Черный для основных линий
    minor_color = (100, 100, 100)  # Серый для промежуточных линий
    bg_color = (255, 255, 255, 200)  # Полупрозрачный белый для фона цифр
    
    # Рисуем основную горизонтальную линию
    draw.line((0, 50, width, 50), fill=main_color, width=2)
    
    # Шаг для основных делений (каждые 10 пикселей)
    major_step = 10
    # Шаг для крупных делений с цифрами (каждые 50 пикселей)
    label_step = 50
    
    # Рисуем деления и цифры
    for x in range(0, width, major_step):
        line_height = 15  # Стандартная высота линии
        
        # Для основных делений с шагом 50 - более заметная линия и цифра
        if x % label_step == 0:
            line_height = 25
            # Белый фон под цифры для четкости
            text_width = 30
            text_height = 16
            draw.rectangle((x-text_width//2, 15, x+text_width//2, 15+text_height), 
                           fill=(255, 255, 255))
            
            # Подпись координаты X
            draw.text((x-12, 15), str(x), font=big_font, fill=(0, 0, 0))
        
        # Рисуем вертикальное деление
        draw.line((x, 50-line_height, x, 50+line_height), 
                  fill=main_color if x % label_step == 0 else minor_color, 
                  width=2 if x % label_step == 0 else 1)
    
    # Рисуем линейку с шагом 100 внизу для удобства
    draw.line((0, 100, width, 100), fill=main_color, width=2)
    
    for x in range(0, width, 100):
        # Вертикальное деление для шага 100
        draw.line((x, 100-20, x, 100+20), fill=main_color, width=2)
        
        # Белый фон под цифры
        text_width = 40
        text_height = 20
        draw.rectangle((x-text_width//2, 120, x+text_width//2, 120+text_height), 
                       fill=(255, 255, 255))
        
        # Крупная цифра с шагом 100
        draw.text((x-15, 120), str(x), font=big_font, fill=(0, 0, 0))
    
    # Создаем директорию, если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Сохраняем результат
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'readable_ruler_{width}_{timestamp}.png')
    img.save(output_path)
    
    print(f'Четкая линейка создана и сохранена в: {output_path}')
    return output_path

def create_vertical_ruler(height=1200, width=100, output_dir='generated_docs'):
    """
    Создает читабельную вертикальную линейку с четкими цифрами.
    
    Args:
        height: Высота линейки в пикселях
        width: Ширина линейки в пикселях
        output_dir: Директория для сохранения результата
    
    Returns:
        str: Путь к сохраненному файлу
    """
    # Создаем белый холст
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать Arial или системный шрифт
    try:
        system_font = Path('C:/Windows/Fonts/arial.ttf')
        if system_font.exists():
            font_path = system_font
        else:
            if not os.path.exists('fonts'):
                os.makedirs('fonts')
            font_path = Path('fonts/arial.ttf')
        
        # Используем достаточно большой шрифт для цифр
        big_font = ImageFont.truetype(str(font_path), 14)
        small_font = ImageFont.truetype(str(font_path), 10)
    except Exception:
        # Если не получилось загрузить шрифт, используем стандартный
        big_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Настройки линейки
    main_color = (0, 0, 0)         # Черный для основных линий
    minor_color = (100, 100, 100)  # Серый для промежуточных линий
    
    # Рисуем основную вертикальную линию
    draw.line((50, 0, 50, height), fill=main_color, width=2)
    
    # Шаг для основных делений (каждые 10 пикселей)
    major_step = 10
    # Шаг для крупных делений с цифрами (каждые 50 пикселей)
    label_step = 50
    
    # Рисуем деления и цифры
    for y in range(0, height, major_step):
        line_width = 15  # Стандартная длина линии
        
        # Для основных делений с шагом 50 - более заметная линия и цифра
        if y % label_step == 0:
            line_width = 25
            # Белый фон под цифры для четкости
            text_width = 30
            text_height = 16
            draw.rectangle((15, y-text_height//2, 15+text_width, y+text_height//2), 
                          fill=(255, 255, 255))
            
            # Подпись координаты Y
            draw.text((15, y-8), str(y), font=big_font, fill=(0, 0, 0))
        
        # Рисуем горизонтальное деление
        draw.line((50-line_width, y, 50+line_width, y), 
                 fill=main_color if y % label_step == 0 else minor_color, 
                 width=2 if y % label_step == 0 else 1)
    
    # Создаем директорию, если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Сохраняем результат
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'vertical_ruler_{height}_{timestamp}.png')
    img.save(output_path)
    
    print(f'Вертикальная линейка создана и сохранена в: {output_path}')
    return output_path

if __name__ == "__main__":
    # Создаем линейки для типичного размера шаблона корочки (1684x1190)
    h_path = create_readable_ruler(width=1684)
    v_path = create_vertical_ruler(height=1190)
    
    # Пытаемся открыть файлы для просмотра
    try:
        import platform
        import subprocess
        
        print("Открываю линейки для просмотра...")
        if platform.system() == 'Windows':
            os.startfile(h_path)
            os.startfile(v_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', h_path])
            subprocess.call(['open', v_path])
        else:  # Linux
            subprocess.call(['xdg-open', h_path])
            subprocess.call(['xdg-open', v_path])
    except Exception as e:
        print(f"Ошибка при открытии файлов: {e}") 