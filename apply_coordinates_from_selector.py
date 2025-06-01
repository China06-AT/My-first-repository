#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re

def apply_coordinates_to_generator(json_file='coordinates.json', generator_file='image_certificate_generator.py'):
    """
    Интегрирует координаты из JSON-файла, созданного HTML-инструментом, 
    в файл генератора image_certificate_generator.py
    
    Args:
        json_file: Путь к JSON-файлу с координатами
        generator_file: Путь к файлу генератора сертификатов
    
    Returns:
        bool: Успешность операции
    """
    print(f"Интеграция координат из {json_file} в {generator_file}...")
    
    # Проверяем наличие файлов
    if not os.path.exists(json_file):
        print(f"ОШИБКА: Файл с координатами {json_file} не найден!")
        return False
    
    if not os.path.exists(generator_file):
        print(f"ОШИБКА: Файл генератора {generator_file} не найден!")
        return False
    
    try:
        # Загружаем координаты из JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            coordinates = json.load(f)
        
        print(f"Координаты успешно загружены из {json_file}")
        
        # Считываем содержимое файла генератора
        with open(generator_file, 'r', encoding='utf-8') as f:
            generator_content = f.read()
        
        # Найдем начало и конец блока COORDINATES
        coordinates_pattern = r'(    COORDINATES = \{.*?\n    \})'
        match = re.search(coordinates_pattern, generator_content, re.DOTALL)
        
        if not match:
            print("ОШИБКА: Не удалось найти блок COORDINATES в файле генератора")
            return False
        
        # Получаем существующий блок с координатами
        existing_block = match.group(1)
        
        # Создаем обновленный блок с новыми координатами
        updated_block = "    COORDINATES = {\n"
        
        # Сохраняем существующие основные секции
        existing_sections = re.findall(r'        # (.*?)\n        \'([^\']+)\': \{(.*?)        \},?', 
                                     existing_block, re.DOTALL)
        
        # Добавляем существующие секции
        for desc, name, content in existing_sections:
            # Пропускаем шаблоны, которые будут заменены новыми координатами
            if name in coordinates:
                continue
            
            updated_block += f"        # {desc}\n"
            updated_block += f"        '{name}': {{{content}        }},\n"
        
        # Добавляем новые координаты
        for template_name, sections in coordinates.items():
            updated_block += f"        # Координаты для {template_name}\n"
            updated_block += f"        '{template_name}': {{\n"
            
            for section, fields in sections.items():
                updated_block += f"            '{section}': {{\n"
                
                for field, coords in fields.items():
                    # Преобразуем массив JavaScript в кортеж Python
                    coord_tuple = tuple(coords)
                    field_desc = get_field_description(field)
                    updated_block += f"                '{field}': {coord_tuple},  # {field_desc}\n"
                
                # Закрываем секцию
                if section == list(sections.keys())[-1]:
                    updated_block += "            }\n"
                else:
                    updated_block += "            },\n"
            
            # Закрываем шаблон
            if template_name == list(coordinates.keys())[-1]:
                updated_block += "        }\n"
            else:
                updated_block += "        },\n"
        
        updated_block += "    }"
        
        # Заменяем старый блок на новый
        updated_content = generator_content.replace(existing_block, updated_block)
        
        # Создаем резервную копию оригинального файла
        backup_file = f"{generator_file}.bak"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(generator_content)
        print(f"Создана резервная копия файла: {backup_file}")
        
        # Записываем обновленное содержимое
        with open(generator_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"Координаты успешно интегрированы в {generator_file}")
        return True
    
    except Exception as e:
        print(f"Ошибка при интеграции координат: {str(e)}")
        return False

def get_field_description(field):
    """Возвращает описание поля для комментария"""
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
    # Запросим путь к файлу JSON с координатами
    print("Интеграция координат с HTML-инструмента в генератор сертификатов")
    print("=" * 70)
    
    json_file = input("Введите путь к JSON-файлу с координатами [coordinates.json]: ").strip()
    if not json_file:
        json_file = "coordinates.json"
    
    generator_file = input("Введите путь к файлу генератора [image_certificate_generator.py]: ").strip()
    if not generator_file:
        generator_file = "image_certificate_generator.py"
    
    result = apply_coordinates_to_generator(json_file, generator_file)
    
    if result:
        print("=" * 70)
        print("✅ Координаты успешно интегрированы!")
        print("Проверьте результат и протестируйте генерацию сертификатов")
    else:
        print("=" * 70)
        print("❌ Не удалось интегрировать координаты")
        print("Проверьте сообщения об ошибках выше") 