#!/usr/bin/env python
# -*- coding: utf-8 -*-

from image_certificate_generator import ImageCertificateGenerator

def main():
    # Создаем экземпляр генератора сертификатов
    generator = ImageCertificateGenerator()
    
    # Параметры сертификата
    width = 1684        # Стандартная ширина шаблона корочки
    height = 1190       # Стандартная высота шаблона корочки
    grid_spacing = 15   # Шаг основной сетки (в пикселях)
    output_prefix = "dense_blank_grid"  # Префикс для выходного файла
    open_file = True    # Автоматически открыть файл после создания
    
    # Создаем пустую координатную сетку с заданными параметрами
    output_path = generator.create_blank_grid(
        width=width,
        height=height,
        grid_spacing=grid_spacing,
        output_prefix=output_prefix,
        open_file=open_file
    )
    
    if output_path:
        print(f"✅ Готово! Пустая координатная сетка успешно создана и сохранена: {output_path}")
    else:
        print("❌ Ошибка создания координатной сетки")

if __name__ == "__main__":
    main() 