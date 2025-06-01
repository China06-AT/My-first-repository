import os
import platform
import subprocess
from datetime import datetime
from image_certificate_generator import ImageCertificateGenerator

def main():
    # Инициализация генератора сертификатов
    generator = ImageCertificateGenerator()
    
    # Параметры для оптимальной сетки
    template_name = 'korotchka'  # Шаблон корочки электробезопасности
    grid_spacing = 20            # Основной шаг сетки (в пикселях)
    minor_grid_step = 5          # Дополнительный шаг сетки (в пикселях)
    grid_opacity = 80            # Прозрачность сетки (0-255)
    show_labels = True           # Показывать подписи координат
    open_file = True             # Открыть файл после создания
    
    # Создание детальной координатной сетки
    output_path = generator.create_detailed_grid(
        template_name=template_name,
        grid_spacing=grid_spacing,
        minor_grid_step=minor_grid_step,
        grid_opacity=grid_opacity,
        show_labels=show_labels,
        output_prefix="detailed_grid",
        open_file=open_file
    )
    
    if output_path:
        print(f"Оптимальная координатная сетка успешно создана: {output_path}")
    else:
        print("Ошибка при создании координатной сетки")

if __name__ == "__main__":
    main() 