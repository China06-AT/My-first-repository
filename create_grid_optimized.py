from image_certificate_generator import ImageCertificateGenerator

def main():
    print("Создание оптимизированной координатной сетки...")
    
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    # Создаем координатную сетку с шагом 25 - оптимальная плотность
    # Не слишком густая, но достаточно точная для работы
    print("\nСоздание координатной сетки с шагом 25 пикселей...")
    
    output_path = generator.create_coordinate_grid(
        template_name="korotchka",
        grid_spacing=25,  # Оптимальный шаг для точности и читабельности
        output_prefix="optimal_grid",  # Префикс для имени файла
        open_file=True    # Автоматически открыть файл
    )
    
    if output_path:
        print(f"\n✅ Координатная сетка успешно создана!")
        print(f"\nПуть к файлу: {output_path}")
    else:
        print(f"\n❌ Ошибка при создании координатной сетки")

if __name__ == "__main__":
    main() 