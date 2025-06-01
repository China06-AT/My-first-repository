from image_certificate_generator import ImageCertificateGenerator
import sys

def show_help():
    print("\nИспользование: python create_detailed_grid.py [параметры]")
    print("\nПараметры:")
    print("  --help                    Показать справку")
    print("  --major=ЧИСЛО             Шаг основных линий сетки в пикселях (по умолчанию 25)")
    print("  --minor=ЧИСЛО             Шаг промежуточных линий (по умолчанию 5)")
    print("  --markers                 Отобразить маркеры координат")
    print("  --no-open                 Не открывать файл после создания")
    print("\nПримеры:")
    print("  python create_detailed_grid.py --major=25 --minor=5")
    print("  python create_detailed_grid.py --markers")

def main():
    print("Генератор детальной координатной сетки для сертификатов")
    
    # Параметры по умолчанию
    major_spacing = 25  # Шаг основных линий
    minor_spacing = 5   # Шаг промежуточных линий
    show_markers = False
    open_file = True
    
    # Разбор аргументов командной строки
    args = sys.argv[1:]
    if not args:
        show_help()
        return
    
    for arg in args:
        if arg == "--help":
            show_help()
            return
        elif arg.startswith("--major="):
            try:
                major_spacing = int(arg.split("=")[1])
            except ValueError:
                print(f"Ошибка: значение шага сетки должно быть числом")
                return
        elif arg.startswith("--minor="):
            try:
                minor_spacing = int(arg.split("=")[1])
            except ValueError:
                print(f"Ошибка: значение промежуточного шага должно быть числом")
                return
        elif arg == "--markers":
            show_markers = True
        elif arg == "--no-open":
            open_file = False
    
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    if show_markers:
        print(f"\nСоздание тестовой координатной сетки с маркерами...")
        output_path = generator.test_coordinates(
            grid_density=major_spacing,
            open_file=open_file
        )
    else:
        # Используем новый метод для создания детальной сетки
        img, temp_png, scale_factor = generator._convert_pdf_to_image(
            generator.template_paths['Курс по электробезопасности']['korotchka']
        )
        
        if img:
            # Применяем детальную сетку
            img = generator._draw_detailed_coordinate_grid(
                img, 
                scale_factor, 
                major_spacing  # Основной шаг
            )
            
            # Сохраняем и открываем результат
            timestamp = generator.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"detailed_grid_{major_spacing}_{timestamp}"
            output_path = generator._save_image(img, output_filename, temp_png)
            
            # Открываем файл если нужно
            if open_file and output_path:
                try:
                    print("Открываю файл для просмотра...")
                    if generator.platform.system() == 'Windows':
                        generator.os.startfile(output_path)
                    elif generator.platform.system() == 'Darwin':  # macOS
                        generator.subprocess.call(['open', str(output_path)])
                    else:  # Linux
                        generator.subprocess.call(['xdg-open', str(output_path)])
                except Exception as e:
                    print(f"Ошибка при открытии файла: {e}")
        else:
            print("Не удалось создать изображение из шаблона")
            output_path = None
    
    if output_path:
        print(f"\n✅ Детальная сетка успешно создана!")
        print(f"\nПуть к файлу: {output_path}")
    else:
        print(f"\n❌ Ошибка при создании детальной сетки")

if __name__ == "__main__":
    main() 