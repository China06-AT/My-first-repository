#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import subprocess
import platform
from image_certificate_generator import ImageCertificateGenerator

def update_coordinates_for_template():
    """
    Позволяет обновить координаты для шаблона и сразу проверить их на тестовом сертификате
    """
    # Путь к шаблону
    template_path = "Безопастность_и_охрана_труда_корочка_1.pdf"
    
    # Проверяем наличие файла
    if not os.path.exists(template_path):
        print(f"ОШИБКА: Файл шаблона {template_path} не найден!")
        return
    
    # Получаем имя шаблона из имени файла
    template_name = os.path.basename(template_path).split('.')[0].upper().replace(' ', '_')
    print(f"Имя шаблона: {template_name}")
    
    # Создаем новые координаты на основе анализа шаблона
    # 👇 ЗДЕСЬ НЕОБХОДИМО ВВЕСТИ ПРАВИЛЬНЫЕ КООРДИНАТЫ ПОСЛЕ АНАЛИЗА ШАБЛОНА 👇
    coordinates = {
        template_name: {
            'LEFT': {
                # Обновите эти координаты согласно вашему шаблону
                'protocol_number': (440, 440),  # Номер удостоверения
                'workplace': (320, 280),        # Организация 
                'fullname': (320, 240),         # ФИО
                'job_title': (320, 320),        # Должность
                'cert_day': (273, 345),         # День выдачи
                'cert_month': (295, 345),       # Месяц выдачи
                'cert_year': (339, 345)         # Год выдачи
            },
            'RIGHT': {
                'cert_date': (733, 377),       # Дата проверки
                'reason': (803, 377),          # Причина проверки 
                'mark': (947, 377),            # Оценка
                'next_date': (1085, 377)       # Дата следующей проверки
            }
        }
    }
    
    # Сохраняем координаты в JSON
    with open(f"coordinates_{template_name}.json", 'w', encoding='utf-8') as f:
        json.dump(coordinates, f, ensure_ascii=False, indent=4)
    print(f"Координаты сохранены в файл: coordinates_{template_name}.json")
    
    # Создаем генератор сертификатов
    generator = ImageCertificateGenerator()
    
    # Обновляем координаты в генераторе
    for template, sections in coordinates.items():
        if template not in generator.COORDINATES:
            generator.COORDINATES[template] = {}
        
        for section, fields in sections.items():
            if section not in generator.COORDINATES[template]:
                generator.COORDINATES[template][section] = {}
            
            for field, coords in fields.items():
                generator.COORDINATES[template][section][field] = coords
    
    # Создаем тестовые данные
    test_data = {
        'protocol_number': '123-456',
        'workplace': 'ТОО "Энергосервис"',
        'fullname': 'Иванов Иван Иванович',
        'job_title': 'Инженер-электрик',
        'cert_date': '12.04.2025',
        'next_date': '12.04.2026',
        'group': ''  # Пустая группа для БиОТ
    }
    
    # Создаем отладочный сертификат с координатной сеткой
    output_debug_path = generator._create_electrobez_korotchka(
        template_path=template_path,
        data=test_data,
        output_filename=f"debug_{template_name}",
        debug_mode=True,
        grid_density=20
    )
    
    print(f"Создан отладочный сертификат с сеткой: {output_debug_path}")
    
    # Создаем финальный сертификат
    output_path = generator._create_electrobez_korotchka(
        template_path=template_path,
        data=test_data,
        output_filename=f"final_{template_name}",
        debug_mode=False,
        grid_density=0
    )
    
    print(f"Создан тестовый сертификат: {output_path}")
    
    # Открываем созданный файл
    try:
        if platform.system() == "Windows":
            os.startfile(output_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", output_path])
        else:  # Linux
            subprocess.call(["xdg-open", output_path])
    except Exception as e:
        print(f"Не удалось открыть файл: {e}")
    
    print("\nИнструкция:")
    print("1. Просмотрите созданный файл debug_{}.jpg с координатной сеткой".format(template_name))
    print("2. Обновите координаты в скрипте (секция coordinates)")
    print("3. Запустите скрипт снова для проверки новых координат")
    print("4. Повторяйте шаги 2-3, пока не получите идеальный результат")
    print("5. Готовые координаты скопируйте в файл image_certificate_generator.py")

if __name__ == "__main__":
    update_coordinates_for_template() 