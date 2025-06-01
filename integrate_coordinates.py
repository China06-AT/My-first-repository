#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from image_certificate_generator import ImageCertificateGenerator

def integrate_coordinates():
    """
    Интегрирует координаты из JSON файла в основной генератор сертификатов
    """
    # Путь к координатам
    json_file = "coordinates_БЕЗОПАСТНОСТЬ_И_ОХРАНА_ТРУДА_КОРОЧКА_1.json"
    
    # Проверяем наличие файла с координатами
    if not os.path.exists(json_file):
        print(f"ОШИБКА: Файл с координатами {json_file} не найден!")
        return
    
    # Загружаем координаты из JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            coordinates = json.load(f)
        print(f"Координаты успешно загружены из {json_file}")
    except Exception as e:
        print(f"Ошибка при загрузке координат: {e}")
        return
    
    # Создаем код для вставки в image_certificate_generator.py
    code = "# Обновленные координаты для шаблона\n"
    code += "COORDINATES = {\n"
    
    # Добавляем существующие координаты (электробезопасность)
    code += "    # Левая часть для электробезопасности\n"
    code += "    'LEFT': {\n"
    code += "        'protocol_number': (257, 75),  # Номер удостоверения\n"
    code += "        'workplace': (260, 115),       # Организация \n"
    code += "        'fullname': (260, 155),        # ФИО\n"
    code += "        'job_title': (260, 225),       # Должность\n"
    code += "        'group_text': (190, 300),      # Группа допуска\n"
    code += "        'cert_day': (273, 345),        # День выдачи\n"
    code += "        'cert_month': (295, 345),      # Месяц выдачи\n"
    code += "        'cert_year': (339, 345)        # Год выдачи\n"
    code += "    },\n"
    code += "    # Правая часть (таблица) для электробезопасности\n"
    code += "    'RIGHT': {\n"
    code += "        'cert_date': (868, 155),      # Дата проверки\n"
    code += "        'reason': (949, 155),         # Причина проверки\n"
    code += "        'group': (1065, 155),         # Группа (римская)\n"
    code += "        'mark': (1156, 155),          # Оценка\n"
    code += "        'next_date': (1246, 155)      # Дата следующей проверки\n"
    code += "    },\n"
    
    # Добавляем координаты для OHRANA_TRUDA (старый шаблон)
    code += "    # Координаты для Безопасности и Охраны труда (старый шаблон)\n"
    code += "    'OHRANA_TRUDA': {\n"
    code += "        'LEFT': {\n"
    code += "            'protocol_number': (440, 440),  # Номер удостоверения\n"
    code += "            'workplace': (320, 280),       # Организация \n"
    code += "            'fullname': (260, 155),        # ФИО\n"
    code += "            'job_title': (280,240),       # Должность\n"
    code += "            'cert_day': (273, 345),        # День выдачи\n"
    code += "            'cert_month': (295, 345),      # Месяц выдачи\n"
    code += "            'cert_year': (339, 345)        # Год выдачи\n"
    code += "        },\n"
    code += "        'RIGHT': {\n"
    code += "            'cert_date': (868, 155),      # Дата проверки\n"
    code += "            'reason': (949, 155),         # Причина проверки\n"
    code += "            'mark': (1156, 155),          # Оценка\n"
    code += "            'next_date': (1246, 155)      # Дата следующей проверки\n"
    code += "        }\n"
    code += "    },\n"
    
    # Добавляем новые координаты из JSON
    for template, sections in coordinates.items():
        code += f"    # Координаты для {template} (новый шаблон)\n"
        code += f"    '{template}': {{\n"
        
        for section, fields in sections.items():
            code += f"        '{section}': {{\n"
            
            for field, coords in fields.items():
                code += f"            '{field}': {tuple(coords) if isinstance(coords, list) else coords},  # {get_field_description(field)}\n"
            
            # Закрываем секцию
            if section == list(sections.keys())[-1]:
                code += "        }\n"
            else:
                code += "        },\n"
        
        # Закрываем шаблон
        code += "    }\n"
        
    # Закрываем словарь
    code += "}\n"
    
    # Сохраняем код в файл
    with open("updated_coordinates.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    print("Код для обновления координат сохранен в файл updated_coordinates.py")
    print("\nИнструкция:")
    print("1. Проверьте сгенерированный код в файле updated_coordinates.py")
    print("2. Замените константу COORDINATES в файле image_certificate_generator.py")
    print("3. Тестируйте новый генератор с обновленными координатами")

def get_field_description(field):
    """Возвращает описание поля по его имени"""
    descriptions = {
        'protocol_number': 'Номер удостоверения',
        'workplace': 'Организация',
        'fullname': 'ФИО',
        'job_title': 'Должность',
        'group_text': 'Группа допуска',
        'cert_day': 'День выдачи',
        'cert_month': 'Месяц выдачи',
        'cert_year': 'Год выдачи',
        'cert_date': 'Дата проверки',
        'reason': 'Причина проверки',
        'group': 'Группа (римская)',
        'mark': 'Оценка',
        'next_date': 'Дата следующей проверки'
    }
    return descriptions.get(field, field)

if __name__ == "__main__":
    integrate_coordinates() 