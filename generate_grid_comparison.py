from datetime import datetime, timedelta
from image_certificate_generator import ImageCertificateGenerator
import os
import sys

def main():
    print("Генерация двух сертификатов для сравнения координатной сетки...")
    
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
    
    # 1. Создаем версию БЕЗ координатной сетки
    print("\n1. Создание сертификата БЕЗ координатной сетки...")
    result1, files1 = generator.generate_document(
        test_data, 
        debug_mode=False
    )
    
    # 2. Создаем версию С координатной сеткой (реже линии)
    print("\n2. Создание сертификата С координатной сеткой (разреженная)...")
    result2, files2 = generator.generate_document(
        {**test_data, 'fullname': test_data['fullname'] + ' (с сеткой)'},
        debug_mode=True, 
        grid_density=200  # Большое значение = реже линии
    )
    
    if result1 and files1 and result2 and files2:
        print("\n✅ Оба сертификата успешно созданы!")
        print(f"\nСертификат БЕЗ сетки: {files1[0]}")
        print(f"\nСертификат С сеткой: {files2[0]}")
        
        # Попытка открыть файлы
        try:
            print("\nОткрытие файлов для просмотра...")
            for file in files1 + files2:
                os.system(f'start "" "{file}"')
        except:
            print("Невозможно автоматически открыть файлы. Пожалуйста, найдите их вручную в папке generated_docs.")
    else:
        print("❌ Ошибка создания сертификатов")
        if not (result1 and files1):
            print("  - Не удалось создать сертификат без сетки")
        if not (result2 and files2):
            print("  - Не удалось создать сертификат с сеткой")

if __name__ == "__main__":
    main() 