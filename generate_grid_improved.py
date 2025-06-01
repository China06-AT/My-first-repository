from datetime import datetime, timedelta
from image_certificate_generator import ImageCertificateGenerator
import os
import subprocess
import platform

def main():
    print("Генерация сертификата с улучшенной координатной сеткой...")
    
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
    
    # Создаем версию с улучшенной координатной сеткой
    print("\nСоздание сертификата с новой улучшенной сеткой...")
    
    # Используем grid_density=150 для более оптимального отображения
    result, files = generator.generate_document(
        test_data,
        debug_mode=True, 
        grid_density=150  # Оптимальная плотность сетки
    )
    
    if result and files:
        print(f"\n✅ Сертификат успешно создан!\n")
        output_file = files[0]
        print(f"Путь к файлу: {output_file}")
        
        # Пытаемся открыть файл в соответствии с ОС
        try:
            print("\nОткрываю файл для просмотра...")
            if platform.system() == 'Windows':
                os.startfile(output_file)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', output_file])
            else:  # Linux и другие
                subprocess.call(['xdg-open', output_file])
            print("Файл открыт. Закройте его после просмотра.")
        except Exception as e:
            print(f"Не удалось автоматически открыть файл: {e}")
            print(f"Пожалуйста, откройте файл вручную: {output_file}")
    else:
        print("❌ Ошибка создания сертификата")

if __name__ == "__main__":
    main() 