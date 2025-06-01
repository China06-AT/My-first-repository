from image_certificate_generator import ImageCertificateGenerator
import sys

def show_help():
    print("\nИспользование: python create_grid.py [параметры]")
    print("\nПараметры:")
    print("  --help                    Показать справку")
    print("  --template=НАЗВАНИЕ       Шаблон для сетки (korotchka)")
    print("  --spacing=ЧИСЛО           Шаг сетки в пикселях (по умолчанию 37)")
    print("  --blank                   Создать пустую сетку без шаблона")
    print("  --no-open                 Не открывать файл после создания")
    print("\nПримеры:")
    print("  python create_grid.py --template=korotchka --spacing=37")
    print("  python create_grid.py --blank --spacing=50")

def main():
    print("Генератор координатной сетки для сертификатов")
    
    # Параметры по умолчанию
    template = "korotchka"
    spacing = 37
    blank = False
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
        elif arg.startswith("--template="):
            template = arg.split("=")[1]
        elif arg.startswith("--spacing="):
            try:
                spacing = int(arg.split("=")[1])
            except ValueError:
                print(f"Ошибка: значение шага сетки должно быть числом")
                return
        elif arg == "--blank":
            blank = True
        elif arg == "--no-open":
            open_file = False
    
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    if blank:
        print(f"\nСоздание пустой координатной сетки с шагом {spacing}...")
        output_path = generator.create_blank_grid(
            grid_spacing=spacing,
            open_file=open_file
        )
    else:
        print(f"\nСоздание координатной сетки для шаблона '{template}' с шагом {spacing}...")
        output_path = generator.create_coordinate_grid(
            template_name=template,
            grid_spacing=spacing, 
            open_file=open_file
        )
    
    if output_path:
        print(f"\n✅ Сетка успешно создана!")
        print(f"\nПуть к файлу: {output_path}")
    else:
        print(f"\n❌ Ошибка при создании координатной сетки")

if __name__ == "__main__":
    main() 