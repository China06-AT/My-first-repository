#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from image_certificate_generator import ImageCertificateGenerator

def update_template_coordinates():
    """
    Обновляет координаты для шаблона 'Безопастность_и_охрана_труда_корочка_1.pdf'
    """
    # Задаем имя шаблона
    template_name = "OHRANA_TRUDA_NEW"
    
    # Создаем новые координаты
    # Это примерные координаты, которые нужно будет обновить после просмотра сетки
    new_coordinates = {
        template_name: {
            'LEFT': {
                'protocol_number': (290, 303),  # Номер удостоверения
                'workplace': (173, 340),        # Организация 
                'fullname': (173, 373),         # ФИО
                'job_title': (173, 406),        # Должность
                'cert_day': (254, 530),         # День выдачи
                'cert_month': (283, 530),       # Месяц выдачи
                'cert_year': (375, 530)         # Год выдачи
            },
            'RIGHT': {
                'cert_date': (733, 377),       # Дата проверки
                'reason': (803, 377),          # Причина проверки
                'mark': (947, 377),            # Оценка
                'next_date': (1085, 377)       # Дата следующей проверки
            }
        }
    }
    
    # Получаем генератор сертификатов
    generator = ImageCertificateGenerator()
    
    # Обновляем координаты в генераторе (добавляем новые)
    for template, sections in new_coordinates.items():
        for section, fields in sections.items():
            if template not in generator.COORDINATES:
                generator.COORDINATES[template] = {}
            
            if section not in generator.COORDINATES[template]:
                generator.COORDINATES[template][section] = {}
            
            for field, coords in fields.items():
                generator.COORDINATES[template][section][field] = coords
    
    # Сохраняем координаты в отдельный JSON файл для использования в будущем
    with open('new_coordinates.json', 'w', encoding='utf-8') as f:
        json.dump(new_coordinates, f, ensure_ascii=False, indent=4)
    
    print(f"Координаты для шаблона '{template_name}' обновлены и сохранены в new_coordinates.json")
    
    # Создаем тестовый сертификат с отладочной сеткой, чтобы проверить координаты
    debug_certificate(generator, template_name)
    
def debug_certificate(generator, template_name):
    """
    Создает тестовый сертификат с координатной сеткой для проверки
    """
    # Тестовые данные
    test_data = {
        'protocol_number': '123-456',
        'workplace': 'ТОО "Энергосервис"',
        'fullname': 'Иванов Иван Иванович',
        'job_title': 'Инженер-электрик',
        'cert_date': '12.04.2025',
        'next_date': '12.04.2026',
        'group': ''  # Пустая группа для БиОТ
    }
    
    # Создаем сертификат с отладочной сеткой
    template_path = generator.template_paths['Безопасность и Охрана труда']['korotchka']
    
    # Заменяем шаблон на новый, если файл существует
    new_template = "Безопастность_и_охрана_труда_корочка_1.pdf"
    if os.path.exists(new_template):
        template_path = new_template
    
    # Создаем отладочную версию
    output_path = generator._create_electrobez_korotchka(
        template_path=template_path,
        data=test_data,
        output_filename=f'debug_{template_name}',
        debug_mode=True,
        grid_density=20
    )
    
    print(f"Создан тестовый сертификат с координатной сеткой: {output_path}")
    
    # Открываем файл
    try:
        import platform
        import subprocess
        
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", output_path])
        else:  # Linux
            subprocess.call(["xdg-open", output_path])
    except Exception as e:
        print(f"Не удалось открыть файл: {e}")

if __name__ == "__main__":
    update_template_coordinates() 