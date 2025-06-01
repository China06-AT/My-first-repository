"""
Модуль с точными координатами для полей сертификата электробезопасности.
Координаты определены с шагом 10 пикселей для максимальной точности.
"""

# Координаты для шаблона "korotchka" (электробезопасность)
KOROTCHKA_COORDINATES = {
    # Левая часть корочки
    'LEFT': {
        'protocol_number': (290, 303),  # Номер удостоверения (правее "КУӘЛІК / УДОСТОВЕРЕНИЕ №")
        'workplace': (173, 340),        # Организация (ұйым / организация)
        'fullname': (173, 373),         # ФИО (фамилия, имя, отчество) 
        'job_title': (173, 406),        # Должность (должность, профессия)
        'group_text': (160, 435),       # Группа допуска (в качестве кого)
        'cert_day': (254, 530),         # День выдачи (после "« ")
        'cert_month': (283, 530),       # Месяц выдачи 
        'cert_year': (375, 530)         # Год выдачи (после "20")
    },
    
    # Правая часть корочки (таблица)
    'RIGHT': {
        'cert_date': (733, 377),       # Дата проверки (1 столбец)
        'reason': (803, 377),          # Причина проверки (2 столбец)
        'group': (877, 377),           # Группа римская (3 столбец)
        'mark': (947, 377),            # Оценка (4 столбец)
        'next_date': (1085, 377)       # Дата следующей проверки (5 столбец)
    }
}

def get_coordinates(template_name='korotchka'):
    """
    Возвращает точные координаты для указанного шаблона.
    
    Args:
        template_name: Имя шаблона ('korotchka' для корочки электробезопасности)
        
    Returns:
        dict: Словарь с координатами всех полей
    """
    if template_name == 'korotchka':
        return KOROTCHKA_COORDINATES
    else:
        raise ValueError(f"Неизвестный шаблон: {template_name}")

def update_generator_coordinates(generator, template_name='korotchka'):
    """
    Обновляет координаты в экземпляре ImageCertificateGenerator.
    
    Args:
        generator: Экземпляр класса ImageCertificateGenerator
        template_name: Имя шаблона ('korotchka' для корочки электробезопасности)
    """
    coords = get_coordinates(template_name)
    generator.COORDINATES = coords
    print(f"Координаты успешно обновлены для шаблона '{template_name}'")

if __name__ == "__main__":
    try:
        from image_certificate_generator import ImageCertificateGenerator
        
        # Создаем экземпляр генератора
        gen = ImageCertificateGenerator()
        
        # Обновляем координаты
        update_generator_coordinates(gen)
        
        # Создаем тестовый сертификат с обновленными координатами
        test_data = {
            'protocol_number': '123-456',
            'workplace': 'ТОО "Энергосервис"',
            'fullname': 'Иванов Иван Иванович',
            'job_title': 'Инженер-электрик',
            'group': '3',
            'cert_date': '12.04.2025',
            'next_date': '12.04.2026'
        }
        
        # Создаем сертификат с отладочной сеткой
        template_path = gen.template_paths['Курс по электробезопасности']['korotchka']
        output_path = gen._create_electrobez_korotchka(
            template_path=template_path,
            data=test_data,
            output_filename='final_certificate',
            debug_mode=True,
            grid_density=50
        )
        
        print(f"Создан тестовый сертификат с точными координатами: {output_path}")
        
    except Exception as e:
        print(f"Ошибка: {e}") 