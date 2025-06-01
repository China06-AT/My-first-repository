#!/usr/bin/env python
# -*- coding: utf-8 -*-

from image_certificate_generator import ImageCertificateGenerator

def main():
    # Создаем экземпляр генератора сертификатов
    generator = ImageCertificateGenerator()
    
    # Оптимальные параметры для плотной, но читабельной сетки
    template_name = 'korotchka'    # Шаблон корочки электробезопасности
    grid_spacing = 15              # Шаг основной сетки (в пикселях)
    minor_grid_step = 5            # Шаг дополнительной сетки (в пикселях)
    grid_opacity = 90              # Прозрачность сетки (0-255)
    show_labels = True             # Показывать подписи координат
    output_prefix = "dense_grid"   # Префикс для выходного файла
    open_file = True               # Автоматически открыть файл после создания
    
    # Создаем детальную сетку с заданными параметрами
    output_path = generator.create_detailed_grid(
        template_name=template_name,
        grid_spacing=grid_spacing,
        minor_grid_step=minor_grid_step,
        grid_opacity=grid_opacity,
        show_labels=show_labels,
        output_prefix=output_prefix,
        open_file=open_file
    )
    
    if output_path:
        print(f"✅ Готово! Координатная сетка успешно создана и сохранена: {output_path}")
    else:
        print("❌ Ошибка создания координатной сетки")

if __name__ == "__main__":
    main() 