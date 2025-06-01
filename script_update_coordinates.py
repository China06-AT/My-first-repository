import json
import re
import sys
import os

def main():
    """
    Скрипт для обновления координат в image_certificate_generator.py
    Использование: python script_update_coordinates.py coordinates_data.json
    """
    
    if len(sys.argv) < 2:
        print("Ошибка: не указан файл с координатами")
        print("Использование: python script_update_coordinates.py coordinates_data.json")
        return 1
    
    coordinates_file = sys.argv[1]
    
    if not os.path.exists(coordinates_file):
        print(f"Ошибка: файл {coordinates_file} не найден")
        return 1
    
    # Загружаем координаты из JSON-файла
    with open(coordinates_file, 'r', encoding='utf-8') as f:
        try:
            new_coordinates = json.load(f)
        except json.JSONDecodeError:
            print("Ошибка: неверный формат JSON")
            return 1
    
    # Проверяем наличие файла генератора
    generator_file = 'image_certificate_generator.py'
    if not os.path.exists(generator_file):
        print(f"Ошибка: файл {generator_file} не найден")
        return 1
    
    # Читаем содержимое файла
    with open(generator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем блок с координатами
    coordinates_pattern = r'COORDINATES\s*=\s*{[^{}]*(?:{[^{}]*(?:{[^{}]*})*[^{}]*})*[^{}]*}'
    match = re.search(coordinates_pattern, content, re.DOTALL)
    
    if not match:
        print("Ошибка: блок COORDINATES не найден в файле")
        return 1
    
    # Создаем новый блок координат
    new_coord_block = "COORDINATES = {\n"
    
    for template, sections in new_coordinates.items():
        new_coord_block += f"    # Координаты для шаблона {template}\n"
        new_coord_block += f"    '{template}': {{\n"
        
        for section, elements in sections.items():
            new_coord_block += f"        '{section}': {{\n"
            
            for name, coords in elements.items():
                new_coord_block += f"            '{name}': ({coords[0]}, {coords[1]}),  # {get_element_description(name)}\n"
            
            new_coord_block += "        },\n"
        
        new_coord_block += "    },\n"
    
    new_coord_block += "}"
    
    # Заменяем старый блок на новый
    new_content = content[:match.start()] + new_coord_block + content[match.end():]
    
    # Записываем изменения обратно в файл
    with open(generator_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Координаты успешно обновлены в файле {generator_file}")
    return 0

def get_element_description(name):
    """Возвращает описание элемента"""
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
    
    return descriptions.get(name, 'Пользовательское поле')

def export_coordinates_from_html(html_file, output_json):
    """
    Экспортирует координаты из HTML-файла в JSON
    Использование: python script_update_coordinates.py --export coordinate_finder.html coordinates.json
    """
    
    if not os.path.exists(html_file):
        print(f"Ошибка: файл {html_file} не найден")
        return 1
    
    # Чтение HTML-файла
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем данные в JavaScript
    coords_pattern = r'let coordinates = (\{[^;]*\});'
    match = re.search(coords_pattern, content, re.DOTALL)
    
    if not match:
        print("Ошибка: данные координат не найдены в HTML")
        return 1
    
    # Попытка извлечь JSON из JavaScript
    js_data = match.group(1)
    # Заменяем одинарные кавычки на двойные для корректного JSON
    js_data = js_data.replace("'", '"')
    
    try:
        coordinates = json.loads(js_data)
    except json.JSONDecodeError:
        print("Ошибка: не удалось преобразовать данные в JSON")
        return 1
    
    # Сохраняем в JSON-файл
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(coordinates, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Координаты успешно экспортированы в {output_json}")
    return 0

if __name__ == "__main__":
    # Проверяем аргументы командной строки для различных режимов работы
    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        if len(sys.argv) < 4:
            print("Ошибка: недостаточно аргументов для экспорта")
            print("Использование: python script_update_coordinates.py --export coordinate_finder.html coordinates.json")
            sys.exit(1)
        sys.exit(export_coordinates_from_html(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(main()) 