from image_certificate_generator import ImageCertificateGenerator
import os
import time

def main():
    print("Создание нескольких вариантов координатной сетки...")
    
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    # Шаги сетки для разных вариантов плотности
    spacings = [20, 25, 30]
    
    results = []
    
    # Создаем сетки с разной плотностью
    for spacing in spacings:
        print(f"\nСоздание координатной сетки с шагом {spacing} пикселей...")
        
        # Используем разные префиксы для легкого различия файлов
        output_path = generator.create_coordinate_grid(
            template_name="korotchka",
            grid_spacing=spacing,
            output_prefix=f"grid_{spacing}px",
            open_file=False  # Не открываем автоматически
        )
        
        if output_path:
            results.append((spacing, output_path))
            print(f"✓ Сетка с шагом {spacing}px создана: {output_path}")
        else:
            print(f"✗ Ошибка при создании сетки с шагом {spacing}px")
        
        # Небольшая пауза между созданием файлов
        time.sleep(1)
    
    print("\n=== Итоговые результаты ===")
    for spacing, path in results:
        print(f"Сетка {spacing}px: {path}")
    
    # Открываем последний вариант (шаг 20px - наиболее точный)
    best_path = next((path for spacing, path in results if spacing == 20), None)
    if best_path and os.path.exists(best_path):
        print(f"\nОткрываю оптимальный вариант сетки (20px)...")
        try:
            os.startfile(best_path)
            print(f"Файл открыт: {best_path}")
        except Exception as e:
            print(f"Не удалось открыть файл: {e}")
            print(f"Пожалуйста, откройте файл вручную: {best_path}")
    
    print("\nРекомендуемый вариант координатной сетки с шагом 20px:")
    if best_path:
        print(f"{best_path}")
    else:
        print("Не удалось создать рекомендуемый вариант")

if __name__ == "__main__":
    main() 