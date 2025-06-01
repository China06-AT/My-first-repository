#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from image_certificate_generator import ImageCertificateGenerator

def apply_coordinates_to_template():
    """
    Применяет координаты к шаблону 'Безопастность_и_охрана_труда_корочка_1.pdf'
    и создает тестовый документ
    """
    # Имя шаблона
    template_name = "OHRANA_TRUDA_NEW"
    
    # Путь к новому шаблону
    template_path = "Безопастность_и_охрана_труда_корочка_1.pdf"
    
    # Проверяем наличие файла шаблона
    if not os.path.exists(template_path):
        print(f"ОШИБКА: Файл шаблона {template_path} не найден!")
        return
    
    # Создаем генератор сертификатов
    generator = ImageCertificateGenerator()
    
    # Загружаем координаты из JSON, если он существует
    if os.path.exists('new_coordinates.json'):
        try:
            with open('new_coordinates.json', 'r', encoding='utf-8') as f:
                coordinates = json.load(f)
            
            # Применяем координаты к генератору
            for template, sections in coordinates.items():
                for section, fields in sections.items():
                    if template not in generator.COORDINATES:
                        generator.COORDINATES[template] = {}
                    
                    if section not in generator.COORDINATES[template]:
                        generator.COORDINATES[template][section] = {}
                    
                    for field, coords in fields.items():
                        generator.COORDINATES[template][section][field] = tuple(coords)
            
            print(f"Координаты из new_coordinates.json успешно загружены")
        except Exception as e:
            print(f"Ошибка загрузки координат: {e}")
    else:
        print("Файл new_coordinates.json не найден, используются стандартные координаты")
    
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
    
    # Создаем тестовый сертификат
    try:
        output_path = generator._create_electrobez_korotchka(
            template_path=template_path,
            data=test_data,
            output_filename=f'test_{template_name}',
            debug_mode=False,  # Без отладочной сетки
            grid_density=0
        )
        
        print(f"Создан тестовый сертификат: {output_path}")
        
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
            
    except Exception as e:
        print(f"Ошибка при создании сертификата: {e}")

if __name__ == "__main__":
    apply_coordinates_to_template() 