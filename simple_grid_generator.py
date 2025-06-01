from datetime import datetime, timedelta
from image_certificate_generator import ImageCertificateGenerator
import os
import platform
import subprocess
from PIL import Image, ImageDraw, ImageFont
import pymupdf

def main():
    print("Генерация сертификата только с координатными линиями...")
    
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    # Путь к PDF-шаблону
    template_path = generator.template_paths['Курс по электробезопасности']['korotchka']
    
    try:
        # Открываем PDF файл
        pdf_document = pymupdf.open(str(template_path))
        page = pdf_document[0]
        zoom = 2
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Создаем временный файл
        temp_png = generator.output_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pix.save(str(temp_png))
        
        # Открываем как PIL Image
        img = Image.open(temp_png)
        pdf_document.close()
        
        # Создаем объект для рисования
        draw = ImageDraw.Draw(img)
        scale_factor = zoom
        
        # НАСТРОЙКИ СЕТКИ
        grid_spacing_x = 75  # Шаг сетки по X
        grid_spacing_y = 75  # Шаг сетки по Y
        grid_color = (150, 150, 150)  # Цвет линий сетки
        label_color = (100, 100, 100)  # Цвет подписей
        
        print(f"Размер изображения: {img.width}x{img.height}")
        print(f"Создание сетки с шагом {grid_spacing_x}x{grid_spacing_y} пикселей")
        
        # Рисуем основные линии
        # Горизонтальные линии
        for y in range(0, img.height, grid_spacing_y):
            draw.line((0, y, img.width, y), fill=grid_color, width=1)
            # Подписываем координаты
            real_y = int(y/scale_factor)
            label_y = f"{real_y}"
            draw.text((5, y+2), label_y, font=generator.fonts['small'], fill=label_color)
        
        # Вертикальные линии
        for x in range(0, img.width, grid_spacing_x):
            draw.line((x, 0, x, img.height), fill=grid_color, width=1)
            # Подписываем координаты
            real_x = int(x/scale_factor)
            label_x = f"{real_x}"
            draw.text((x+2, 5), label_x, font=generator.fonts['small'], fill=label_color)
        
        # Сохраняем результат
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = generator.output_dir / f"grid_only_{timestamp}.jpg"
        
        img.save(str(output_path), quality=95)
        print(f"\n✅ Изображение успешно сохранено в {output_path}")
        
        # Удаляем временный файл PNG
        if os.path.exists(temp_png):
            os.remove(temp_png)
        
        # Пытаемся открыть файл в соответствии с ОС
        try:
            print("\nОткрываю файл для просмотра...")
            if platform.system() == 'Windows':
                os.startfile(output_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', str(output_path)])
            else:  # Linux и другие
                subprocess.call(['xdg-open', str(output_path)])
            print("Файл открыт. Закройте его после просмотра.")
        except Exception as e:
            print(f"Не удалось автоматически открыть файл: {e}")
            print(f"Пожалуйста, откройте файл вручную: {output_path}")
        
        print(f"\nПуть к файлу с координатной сеткой:")
        print(f"{output_path}")
        
    except Exception as e:
        print(f"Ошибка создания сетки: {e}")

if __name__ == "__main__":
    main() 