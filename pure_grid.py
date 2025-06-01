from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from datetime import datetime

def main():
    print("Генерация чистой координатной сетки без содержимого документа...")
    
    # Размер изображения (примерно соответствует размеру документа)
    width = 1684
    height = 1190
    
    # Создаем белый холст
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Настройки сетки
    grid_spacing_x = 75  # Шаг сетки по X
    grid_spacing_y = 75  # Шаг сетки по Y
    grid_color = (150, 150, 150)  # Серый цвет линий
    label_color = (100, 100, 100)  # Темно-серый цвет подписей
    
    # Загружаем шрифт для подписей
    try:
        # Попытка использовать Arial
        font_path = 'C:/Windows/Fonts/arial.ttf'
        font = ImageFont.truetype(font_path, 16)
    except:
        # Если не удалось, используем стандартный шрифт
        font = ImageFont.load_default()
    
    print(f"Создание чистой сетки размером {width}x{height} с шагом {grid_spacing_x}x{grid_spacing_y} пикселей")
    
    # Рисуем горизонтальные линии
    for y in range(0, height, grid_spacing_y):
        draw.line((0, y, width, y), fill=grid_color, width=1)
        # Подписываем координаты (только фактические, без масштабирования)
        label_y = f"{y}"
        draw.text((5, y+2), label_y, font=font, fill=label_color)
    
    # Рисуем вертикальные линии
    for x in range(0, width, grid_spacing_x):
        draw.line((x, 0, x, height), fill=grid_color, width=1)
        # Подписываем координаты
        label_x = f"{x}"
        draw.text((x+2, 5), label_x, font=font, fill=label_color)
    
    # Создаем директорию, если ее нет
    output_dir = Path('generated_docs')
    output_dir.mkdir(exist_ok=True)
    
    # Сохраняем результат
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = output_dir / f"pure_grid_{timestamp}.jpg"
    
    img.save(str(output_path), quality=95)
    print(f"\n✅ Чистая координатная сетка создана и сохранена в {output_path}")
    
    # Пытаемся открыть файл
    try:
        print("\nОткрываю файл для просмотра...")
        os.startfile(output_path)  # Работает на Windows
        print("Файл открыт. Закройте его после просмотра.")
    except Exception as e:
        print(f"Не удалось автоматически открыть файл: {e}")
        print(f"Пожалуйста, откройте файл вручную: {output_path}")
    
    print(f"\nПуть к файлу с чистой координатной сеткой:")
    print(f"{output_path}")

if __name__ == "__main__":
    main() 