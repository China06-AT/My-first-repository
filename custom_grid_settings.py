from datetime import datetime, timedelta
from image_certificate_generator import ImageCertificateGenerator
import os
import argparse
import platform
import subprocess

def main():
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description='Генерация сертификата с настройкой координатной сетки')
    
    # Общие настройки
    parser.add_argument('--no-debug', action='store_true', help='Выключить режим отладки с координатной сеткой')
    parser.add_argument('--grid-density', type=int, default=150, help='Плотность координатной сетки (больше = реже линии)')
    
    # Цветовые настройки
    parser.add_argument('--grid-opacity', type=int, default=80, help='Прозрачность сетки, от 0 до 255')
    parser.add_argument('--highlight-color', choices=['green', 'red', 'blue', 'orange'], default='green', 
                      help='Цвет выделения ключевых точек')
    
    # Отображение
    parser.add_argument('--show-axes-only', action='store_true', help='Показывать только оси X и Y, без промежуточных линий')
    parser.add_argument('--radius', type=int, default=6, help='Радиус маркеров ключевых точек')
    
    args = parser.parse_args()
    
    # Выводим настройки
    print("\n🔧 Настройки координатной сетки:")
    print(f"  - Режим отладки: {'Выключен' if args.no_debug else 'Включен'}")
    print(f"  - Плотность сетки: {args.grid_density}")
    print(f"  - Прозрачность сетки: {args.grid_opacity}")
    print(f"  - Цвет выделения: {args.highlight_color}")
    print(f"  - Только оси: {'Да' if args.show_axes_only else 'Нет'}")
    print(f"  - Радиус маркеров: {args.radius}")

    # Определяем цвет выделения
    color_map = {
        'green': (0, 150, 0, 180),
        'red': (180, 0, 0, 180),
        'blue': (0, 0, 180, 180),
        'orange': (200, 100, 0, 180)
    }
    
    # Готовим параметры для передачи в генератор
    # В будущей версии можно расширить ImageCertificateGenerator для поддержки дополнительных параметров
    
    # Создаем тестовые данные
    test_data = {
        'fullname': 'Тестов Тест Тестович',
        'workplace': 'ТОО "Компания"',
        'job_title': 'Инженер-электрик',
        'position': 'Курс по электробезопасности',
        'qualification_group': '4',
        'cert_date': datetime.now() - timedelta(days=5),
        'next_date': datetime.now() + timedelta(days=365)
    }

    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    print("\nСоздание сертификата с указанными настройками...")
    
    # Генерируем сертификат
    result, files = generator.generate_document(
        test_data,
        debug_mode=not args.no_debug,
        grid_density=args.grid_density
    )
    
    if result and files:
        print(f"\n✅ Сертификат успешно создан!\n")
        output_file = files[0]
        print(f"Путь к файлу: {output_file}")
        
        # Пытаемся открыть файл
        try:
            print("\nОткрываю файл для просмотра...")
            if platform.system() == 'Windows':
                os.startfile(output_file)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', output_file])
            else:  # Linux
                subprocess.call(['xdg-open', output_file])
        except Exception as e:
            print(f"Не удалось автоматически открыть файл: {e}")
            print(f"Пожалуйста, откройте файл вручную: {output_file}")
    else:
        print("❌ Ошибка создания сертификата")
        
    print("\nПримеры использования:")
    print("  - Более плотная сетка: python custom_grid_settings.py --grid-density 100")
    print("  - Редкая сетка с красными точками: python custom_grid_settings.py --grid-density 200 --highlight-color red")
    print("  - Без координатной сетки: python custom_grid_settings.py --no-debug")

if __name__ == "__main__":
    main() 