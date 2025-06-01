#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from image_certificate_generator import ImageCertificateGenerator

def analyze_generator():
    """
    Анализирует ImageCertificateGenerator и выводит информацию
    о том, как программа определяет шаблоны и выбирает координаты
    """
    print("Анализ генератора сертификатов...")
    
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    # Выводим доступные шаблоны
    print("\n1. Доступные шаблоны:")
    for category, templates in generator.template_paths.items():
        print(f"  • {category}:")
        for template_type, path in templates.items():
            print(f"     - {template_type}: {path}")
    
    # Выводим все константы COORDINATES
    print("\n2. Определены координаты для следующих шаблонов:")
    for template_name in generator.COORDINATES:
        print(f"  • {template_name}")
        if isinstance(generator.COORDINATES[template_name], dict):
            if 'LEFT' in generator.COORDINATES[template_name] or 'RIGHT' in generator.COORDINATES[template_name]:
                # Это секции LEFT/RIGHT
                for section in generator.COORDINATES[template_name]:
                    print(f"     - {section}: {len(generator.COORDINATES[template_name][section])} полей")
            else:
                # Это вложенные координаты
                for section in generator.COORDINATES[template_name]:
                    print(f"     - {section}")
    
    # Находим функцию создания сертификата
    print("\n3. Функция выбора координат:")
    
    # Анализируем методы _fill* для определения логики выбора координат
    fill_methods = [
        "_fill_certificate_data", 
        "_fill_left_side",
        "_fill_right_side",
        "_fill_ohrana_truda"
    ]
    
    for method_name in fill_methods:
        if hasattr(generator, method_name):
            method = getattr(generator, method_name)
            print(f"\n • Метод {method_name}:")
            if method.__doc__:
                print(f"   {method.__doc__.strip()}")
            
            # Выводим исходный код метода для анализа
            import inspect
            source = inspect.getsource(method)
            
            # Ищем использование COORDINATES
            coords_usage = re.findall(r'COORDINATES\[[\'"](.*?)[\'"]\]', source)
            if coords_usage:
                print(f"   Использует координаты из: {', '.join(coords_usage)}")
            
            # Ищем условия выбора шаблона
            template_conditions = re.findall(r'if\s+([^:]+)\s*:', source)
            for condition in template_conditions:
                if "template" in condition or "OHRANA_TRUDA" in condition:
                    print(f"   Условие выбора шаблона: {condition.strip()}")
    
    # Предлагаем возможные исправления
    print("\n4. Возможные проблемы и решения:")
    
    # Изменяем каждый метод в зависимости от проблемы
    patch_fill_ohrana_truda(generator)

def patch_fill_ohrana_truda(generator):
    """
    Создает исправленную версию метода _fill_ohrana_truda,
    которая будет правильно определять шаблон из новых координат
    """
    # Проанализируем существующий метод
    import inspect
    if hasattr(generator, "_fill_ohrana_truda"):
        source = inspect.getsource(generator._fill_ohrana_truda)
        
        # Проверяем, использует ли метод жестко заданный ключ 'OHRANA_TRUDA'
        if "COORDINATES['OHRANA_TRUDA']" in source:
            print(" • ПРОБЛЕМА: Метод _fill_ohrana_truda жестко использует ключ 'OHRANA_TRUDA'")
            print("   Это значит, что координаты с другими именами шаблонов игнорируются.")
            print("   РЕШЕНИЕ: Исправим это в файле fix_template_usage.py")
            
            # Создаем исправленный файл
            create_template_fix()
            
            # Создаем батник для запуска исправления
            create_fix_batch()

def create_template_fix():
    """Создает файл с исправлением для проблемы с шаблонами"""
    content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from image_certificate_generator import ImageCertificateGenerator

def fix_template_handling():
    \"""
    Исправляет файл image_certificate_generator.py для работы с новыми шаблонами
    \"""
    print("Исправление обработки шаблонов в image_certificate_generator.py...")
    
    # Путь к файлу генератора
    generator_file = "image_certificate_generator.py"
    
    if not os.path.exists(generator_file):
        print(f"ОШИБКА: Файл {generator_file} не найден!")
        return False
    
    try:
        # Создаем резервную копию
        backup_file = f"{generator_file}.backup"
        import shutil
        shutil.copy2(generator_file, backup_file)
        print(f"Создана резервная копия файла: {backup_file}")
        
        # Считываем содержимое файла
        with open(generator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Исправляем метод _fill_ohrana_truda для динамического определения шаблона
        old_method = re.search(r'def _fill_ohrana_truda\(self, draw, data, scale_factor\):.*?""".*?"""(.*?)def', content, re.DOTALL)
        
        if old_method:
            old_code = old_method.group(1)
            
            # Создаем новую версию метода
            new_code = old_code.replace(
                "coords = self.COORDINATES['OHRANA_TRUDA']['LEFT']", 
                "# Динамически определяем шаблон из переданного пути к файлу или используем OHRANA_TRUDA\\n        "
                "template_name = data.get('template_name', 'OHRANA_TRUDA')\\n        "
                "if template_name in self.COORDINATES:\\n            "
                "coords = self.COORDINATES[template_name]['LEFT']\\n        "
                "else:\\n            "
                "coords = self.COORDINATES['OHRANA_TRUDA']['LEFT']"
            )
            
            # Аналогично заменяем для правой части
            new_code = new_code.replace(
                "right_coords = self.COORDINATES['OHRANA_TRUDA']['RIGHT']", 
                "right_coords = self.COORDINATES[template_name]['RIGHT'] if template_name in self.COORDINATES else self.COORDINATES['OHRANA_TRUDA']['RIGHT']"
            )
            
            # Заменяем в файле
            content = content.replace(old_code, new_code)
            
            # Обновляем метод _create_electrobez_korotchka для передачи имени шаблона
            create_method = re.search(r'def _create_electrobez_korotchka\(self, template_path, data, output_filename, debug_mode=False, grid_density=20\):.*?""".*?"""(.*?)try:', content, re.DOTALL)
            
            if create_method:
                old_create_code = create_method.group(1)
                new_create_code = old_create_code.replace(
                    "# Проверка файла шаблона", 
                    "# Получаем имя шаблона из пути к файлу\\n        "
                    "template_name = os.path.basename(template_path).split('.')[0].upper().replace(' ', '_').replace('-', '_')\\n        "
                    "data['template_name'] = template_name\\n        "
                    "print(f\"Используется шаблон: {template_name}\")\\n        "
                    "# Проверка файла шаблона"
                )
                
                content = content.replace(old_create_code, new_create_code)
            
            # Записываем изменения в файл
            with open(generator_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Исправления успешно применены!")
            print("Теперь генератор будет определять шаблон по имени файла и использовать соответствующие координаты.")
            return True
        else:
            print("❌ Не удалось найти метод _fill_ohrana_truda в файле.")
            return False
    
    except Exception as e:
        print(f"❌ Ошибка при исправлении файла: {e}")
        return False

if __name__ == "__main__":
    fix_template_handling()
"""
    
    with open("fix_template_usage.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"   ✅ Создан файл fix_template_usage.py для исправления проблемы")

def create_fix_batch():
    """Создает батник для запуска исправления"""
    content = """@echo off
echo Исправление обработки шаблонов в генераторе сертификатов...
python fix_template_usage.py
pause
"""
    
    with open("fix_templates.bat", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"   ✅ Создан файл fix_templates.bat для быстрого запуска исправления")

if __name__ == "__main__":
    print("=" * 70)
    print(" АНАЛИЗ И ОТЛАДКА РАСПОЗНАВАНИЯ ШАБЛОНОВ В ГЕНЕРАТОРЕ СЕРТИФИКАТОВ ")
    print("=" * 70)
    
    analyze_generator()
    
    print("\nДля исправления проблемы запустите:")
    print("   fix_templates.bat")
    print("\nПосле этого проверьте координаты с помощью:")
    print("   python test_coordinates.py")
    print("=" * 70) 