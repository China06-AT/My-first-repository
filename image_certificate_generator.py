import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import io
# Правильный импорт PyMuPDF
import pymupdf
import platform
import subprocess

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageCertificateGenerator:
    def __init__(self):
        self.db = sqlite3.connect('certificates.db', check_same_thread=False, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.create_tables()
        
        # Добавляем курс Безопасность и охрана труда
        self.template_paths = {
            'Курс по электробезопасности': {
                'korotchka': Path('Электробез корочка .pdf')
            },
            'Безопасность и Охрана труда': {
                'korotchka': Path('Безопастность и охрана труда корочка.pdf')
            }
        }
        self.output_dir = Path('generated_docs')
        self.output_dir.mkdir(exist_ok=True)
        
        # Настройка шрифтов - важно указать корректные пути и размеры
        self.font_path = Path('fonts/arial.ttf')
        # Если директории с шрифтами не существует, создаем её
        if not os.path.exists('fonts'):
            os.makedirs('fonts')
            
        # Проверяем наличие шрифта, если его нет - ищем в системе
        if not self.font_path.exists():
            # На Windows путь к системным шрифтам
            system_font = Path('C:/Windows/Fonts/arial.ttf')
            if system_font.exists():
                self.font_path = system_font
                logger.info(f"Используем системный шрифт: {self.font_path}")
        
        self.font_sizes = {
            'small': 16,
            'normal': 20,
            'large': 24,
            'xlarge': 28,
            'xxlarge': 32
        }
        
        # Цвета для текста
        self.colors = {
            'black': (0, 0, 0),
            'blue': (0, 0, 128),
            'red': (128, 0, 0)
        }
        
        # Загружаем разные размеры шрифтов
        try:
            self.fonts = {}
            for name, size in self.font_sizes.items():
                self.fonts[name] = ImageFont.truetype(str(self.font_path), size)
            logger.info("Шрифты успешно загружены")
        except Exception as e:
            logger.error(f"Ошибка загрузки шрифтов: {e}")
            # Если шрифты не загрузились, используем стандартный
            self.fonts = {name: ImageFont.load_default() for name, size in self.font_sizes.items()}

    def create_tables(self):
        self.db.execute('''CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocol_number TEXT,
            fullname TEXT,
            workplace TEXT,
            job_title TEXT,
            position TEXT,
            group_number TEXT,
            cert_date DATE,
            next_date DATE,
            template_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        self.db.commit()

    def generate_document(self, data, debug_mode=False, grid_density=200):
        try:
            generated_files = []
            protocol_number = str(self.db.execute("SELECT COUNT(*) FROM certificates").fetchone()[0] + 1).zfill(3)

            if data['position'] == 'Курс по электробезопасности':
                # Генерируем сертификат для электробезопасности (корочку)
                group = data['qualification_group']
                if isinstance(group, str):
                    group = int(group) if group.isdigit() else 0
                
                cert_data = {
                    'fullname': data['fullname'],
                    'workplace': data['workplace'],
                    'job_title': data['job_title'],
                    'what': "и выше" if group in [4, 5] else "",
                    'do': "до " if group in [4, 5] else "",
                    'next_date': data['next_date'].strftime('%d.%m.%Y') if data['next_date'] else "",
                    'protocol_number': protocol_number,
                    'cert_date': data['cert_date'],
                    'group': str(group)
                }
                
                # Создаем Элбез корочку с передачей параметров отладки
                template_path = self.template_paths['Курс по электробезопасности']['korotchka']
                output_path = self._create_electrobez_korotchka(
                    template_path=template_path,
                    data=cert_data,
                    output_filename=f"{data['fullname']}_korotchka",
                    debug_mode=debug_mode,
                    grid_density=grid_density
                )
                if output_path:
                    generated_files.append(output_path)
                    logger.info(f"Успешно создана корочка электробезопасности: {output_path}")
                else:
                    logger.error("Не удалось создать корочку электробезопасности")
            
            elif data['position'] == 'Безопасность и Охрана труда':
                # Генерируем сертификат для безопасности и охраны труда
                cert_data = {
                    'fullname': data['fullname'],
                    'workplace': data['workplace'],
                    'job_title': data['job_title'],
                    'next_date': data['next_date'].strftime('%d.%m.%Y') if data['next_date'] else "",
                    'protocol_number': protocol_number,
                    'cert_date': data['cert_date'],
                    # Для БиОТ группа не требуется, но структура данных одинаковая
                    'group': ""
                }
                
                # Создаем корочку безопасности и охраны труда
                template_path = self.template_paths['Безопасность и Охрана труда']['korotchka']
                output_path = self._create_electrobez_korotchka(
                    template_path=template_path,
                    data=cert_data,
                    output_filename=f"{data['fullname']}_ohrana_truda",
                    debug_mode=debug_mode,
                    grid_density=grid_density
                )
                if output_path:
                    generated_files.append(output_path)
                    logger.info(f"Успешно создана корочка по безопасности и охране труда: {output_path}")
                else:
                    logger.error("Не удалось создать корочку по безопасности и охране труда")

            # Сохраняем в базу данных
            self._save_to_database(data, protocol_number)
            return True, generated_files

        except Exception as e:
            logger.error(f"Ошибка при генерации документа: {str(e)}")
            return False, None

    # Ключевые координаты для размещения текста (X, Y)
    COORDINATES = {
        # Левая часть для электробезопасности
        'LEFT': {
            'protocol_number': (257, 75),  # Номер удостоверения
            'workplace': (260, 115),       # Организация 
            'fullname': (260, 155),        # ФИО
            'job_title': (260, 225),       # Должность
            'group_text': (190, 300),      # Группа допуска
            'cert_day': (273, 345),        # День выдачи
            'cert_month': (295, 345),      # Месяц выдачи
            'cert_year': (339, 345)        # Год выдачи
        },
        # Правая часть (таблица) для электробезопасности
        'RIGHT': {
            'cert_date': (868, 155),      # Дата проверки
            'reason': (949, 155),         # Причина проверки
            'group': (1065, 155),         # Группа (римская)
            'mark': (1156, 155),          # Оценка
            'next_date': (1246, 155)      # Дата следующей проверки
        },
        # Координаты для Безопасности и Охраны труда
        'OHRANA_TRUDA': {
            'LEFT': {
                'protocol_number': (440, 440),  # Номер удостоверения
                'workplace': (320, 280),       # Организация 
                'fullname': (260, 155),        # ФИО
                'job_title': (320,100),       # Должность
                'cert_day': (273, 345),        # День выдачи
                'cert_month': (295, 345),      # Месяц выдачи
                'cert_year': (339, 345)        # Год выдачи
            },
            'RIGHT': {
                'cert_date': (868, 155),      # Дата проверки
                'reason': (949, 155),         # Причина проверки
                'mark': (1156, 155),          # Оценка
                'next_date': (1246, 155)      # Дата следующей проверки
            }
        }
    }

    def _create_electrobez_korotchka(self, template_path, data, output_filename, debug_mode=False, grid_density=20):
        """Создает сертификат корочки электробезопасности"""
        try:
            # Проверка файла шаблона
            if not os.path.exists(template_path):
                logger.error(f"Файл шаблона {template_path} не найден!")
                return None
            
            # Конвертация PDF в изображение
            img, temp_png, scale_factor = self._convert_pdf_to_image(template_path)
            if img is None:
                # В случае ошибки копируем оригинальный PDF
                return self._copy_original_pdf(template_path, output_filename)
            
            # Создаем объект для рисования
            draw = ImageDraw.Draw(img)
            
            # Заполняем данные на изображении
            self._fill_certificate_data(draw, data, scale_factor)
            
            # Добавляем координатную сетку при необходимости
            if debug_mode:
                img = self._draw_coordinate_grid(img, scale_factor, grid_density)
            
            # Сохраняем результат
            output_path = self._save_image(img, output_filename, temp_png)
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка создания корочки: {e}", exc_info=True)
            return self._copy_original_pdf(template_path, output_filename)

    def _convert_pdf_to_image(self, template_path):
        """Конвертирует PDF в изображение"""
        try:
            pdf_document = pymupdf.open(str(template_path))
            page = pdf_document[0]
            zoom = 2  # Масштабный коэффициент для лучшего качества
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Сохраняем во временный файл PNG
            temp_png = self.output_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pix.save(str(temp_png))
            
            img = Image.open(temp_png)
            logger.info(f"PDF конвертирован в изображение размером {img.width}x{img.height}")
            pdf_document.close()
            
            return img, temp_png, zoom
        except Exception as e:
            logger.error(f"Ошибка конвертации PDF в изображение: {e}", exc_info=True)
            return None, None, None

    def _copy_original_pdf(self, template_path, output_filename):
        """Копирует оригинальный PDF файл в случае ошибки конвертации"""
        try:
            import shutil
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"{output_filename}_{timestamp}.pdf"
            shutil.copy2(template_path, output_path)
            return output_path
        except Exception as copy_error:
            logger.error(f"Невозможно скопировать исходный файл: {copy_error}")
            return None
    
    def _fill_certificate_data(self, draw, data, scale_factor):
        """Заполняет все данные на сертификате"""
        # Определяем, какой шаблон используется и выбираем координаты
        if 'group' in data and data['group']:
            # Для электробезопасности с группой
            self._fill_left_side(draw, data, scale_factor)
            self._fill_right_side(draw, data, scale_factor)
        else:
            # Для безопасности и охраны труда
            self._fill_ohrana_truda(draw, data, scale_factor)

    def _fill_left_side(self, draw, data, scale_factor):
        """Заполняет левую часть корочки"""
        coords = self.COORDINATES['LEFT']
        
        # Номер удостоверения
        self._place_text(
            draw, data['protocol_number'], 
            self._scale_coords(coords['protocol_number'], scale_factor), 
            self.fonts['normal'], self.colors['black']
        )

        # Организация
        self._place_centered_text(
            draw, data['workplace'], 
            self._scale_coords(coords['workplace'], scale_factor), 
            330 * scale_factor, self.fonts['normal'], self.colors['black']
        )
        
        # ФИО
        self._place_centered_text(
            draw, data['fullname'], 
            self._scale_coords(coords['fullname'], scale_factor), 
            330 * scale_factor, self.fonts['normal'], self.colors['black']
        )
        
        # Должность
        self._place_centered_text(
            draw, data['job_title'], 
            self._scale_coords(coords['job_title'], scale_factor), 
            330 * scale_factor, self.fonts['normal'], self.colors['black']
        )
        
        # Группа допуска
        group_text = self._format_group_text(data['group'])
        self._place_text(
            draw, group_text, 
            self._scale_coords(coords['group_text'], scale_factor), 
            self.fonts['normal'], self.colors['black']
        )
        
        # Дата выдачи
        if data['cert_date']:
            day, month, year = self._parse_date(data['cert_date'])
            
            # День
            self._place_text(draw, day, 
                self._scale_coords(coords['cert_day'], scale_factor), 
                self.fonts['normal'], self.colors['black'])
            
            # Месяц
            self._place_text(draw, month, 
                self._scale_coords(coords['cert_month'], scale_factor), 
                self.fonts['normal'], self.colors['black'])
            
            # Год (последние 2 цифры)
            self._place_text(draw, year[2:], 
                self._scale_coords(coords['cert_year'], scale_factor), 
                self.fonts['normal'], self.colors['black'])

    def _fill_right_side(self, draw, data, scale_factor):
        """Заполняет правую часть корочки (таблицу)"""
        coords = self.COORDINATES['RIGHT']
        
        # Дата проверки
        if data['cert_date']:
            date_str = data['cert_date'].strftime('%d.%m.%Y') if hasattr(data['cert_date'], 'strftime') else data['cert_date']
            self._place_centered_text(
                draw, date_str, 
                self._scale_coords(coords['cert_date'], scale_factor), 
                80 * scale_factor, self.fonts['small'], self.colors['black']
            )
        
        # Причина проверки (всегда "Первичная")
        self._place_centered_text(
            draw, "Первичная", 
            self._scale_coords(coords['reason'], scale_factor), 
            80 * scale_factor, self.fonts['small'], self.colors['black']
        )
        
        # Группа (римская цифра)
        roman_group = self._to_roman(data['group'])
        self._place_centered_text(
            draw, roman_group, 
            self._scale_coords(coords['group'], scale_factor), 
            80 * scale_factor, self.fonts['small'], self.colors['black']
        )
        
        # Оценка (всегда "Хорошо")
        self._place_centered_text(
            draw, "Хорошо", 
            self._scale_coords(coords['mark'], scale_factor), 
            80 * scale_factor, self.fonts['small'], self.colors['black']
        )
        
        # Дата следующей проверки
        if data['next_date']:
            next_date_str = data['next_date'] if isinstance(data['next_date'], str) else data['next_date'].strftime('%d.%m.%Y')
            self._place_centered_text(
                draw, next_date_str, 
                self._scale_coords(coords['next_date'], scale_factor), 
                80 * scale_factor, self.fonts['small'], self.colors['black']
            )

    def _fill_ohrana_truda(self, draw, data, scale_factor):
        """Заполняет данные для корочки безопасности и охраны труда"""
        coords = self.COORDINATES['OHRANA_TRUDA']['LEFT']
        
        # Номер удостоверения
        self._place_text(
            draw, data['protocol_number'], 
            self._scale_coords(coords['protocol_number'], scale_factor), 
            self.fonts['normal'], self.colors['black']
        )

        # Организация
        self._place_centered_text(
            draw, data['workplace'], 
            self._scale_coords(coords['workplace'], scale_factor), 
            330 * scale_factor, self.fonts['normal'], self.colors['black']
        )
        
        # ФИО
        self._place_centered_text(
            draw, data['fullname'], 
            self._scale_coords(coords['fullname'], scale_factor), 
            330 * scale_factor, self.fonts['normal'], self.colors['black']
        )
        
        # Должность
        self._place_centered_text(
            draw, data['job_title'], 
            self._scale_coords(coords['job_title'], scale_factor), 
            330 * scale_factor, self.fonts['normal'], self.colors['black']
        )
        
        # Дата выдачи
        if data['cert_date']:
            day, month, year = self._parse_date(data['cert_date'])
            
            # День
            self._place_text(draw, day, 
                self._scale_coords(coords['cert_day'], scale_factor), 
                self.fonts['normal'], self.colors['black'])
            
            # Месяц
            self._place_text(draw, month, 
                self._scale_coords(coords['cert_month'], scale_factor), 
                self.fonts['normal'], self.colors['black'])
            
            # Год (последние 2 цифры)
            self._place_text(draw, year[2:], 
                self._scale_coords(coords['cert_year'], scale_factor), 
                self.fonts['normal'], self.colors['black'])
        
        # Заполняем правую часть
        right_coords = self.COORDINATES['OHRANA_TRUDA']['RIGHT']
        
        # Дата проверки
        if data['cert_date']:
            date_str = data['cert_date'].strftime('%d.%m.%Y') if hasattr(data['cert_date'], 'strftime') else data['cert_date']
            self._place_centered_text(
                draw, date_str, 
                self._scale_coords(right_coords['cert_date'], scale_factor), 
                80 * scale_factor, self.fonts['small'], self.colors['black']
            )
        
        # Причина проверки (всегда "Первичная")
        self._place_centered_text(
            draw, "Первичная", 
            self._scale_coords(right_coords['reason'], scale_factor), 
            80 * scale_factor, self.fonts['small'], self.colors['black']
        )
        
        # Оценка (всегда "Хорошо")
        self._place_centered_text(
            draw, "Хорошо", 
            self._scale_coords(right_coords['mark'], scale_factor), 
            80 * scale_factor, self.fonts['small'], self.colors['black']
        )
        
        # Дата следующей проверки
        if data['next_date']:
            next_date_str = data['next_date'] if isinstance(data['next_date'], str) else data['next_date'].strftime('%d.%m.%Y')
            self._place_centered_text(
                draw, next_date_str, 
                self._scale_coords(right_coords['next_date'], scale_factor), 
                80 * scale_factor, self.fonts['small'], self.colors['black']
            )

    def _scale_coords(self, coords, scale_factor):
        """Масштабирует координаты"""
        return (coords[0] * scale_factor, coords[1] * scale_factor)

    def _format_group_text(self, group):
        """Форматирует текст группы по электробезопасности"""
        try:
            if not group:  # Для безопасности и охраны труда группа отсутствует
                return ""
                
            group_num = int(group)
            if group_num in [2, 3]:
                return f"{group_num} гр. 1000В и ниже"
            elif group_num in [4, 5]:
                return f"{group_num} гр. 1000В и выше"
            else:
                return f"{group_num} гр."
        except (ValueError, TypeError):
            return f"{group} гр."

    def _parse_date(self, date_value):
        """Разбирает дату на компоненты (день, месяц, год)"""
        try:
            if not date_value:  # Проверка на пустое значение
                return "", "", ""
                
            if isinstance(date_value, str):
                date_parts = date_value.split('.')
                if len(date_parts) == 3:
                    return date_parts[0], date_parts[1], date_parts[2]
                else:
                    # Некорректный формат даты - возвращаем безопасные значения
                    logger.warning(f"Некорректный формат даты: {date_value}")
                    return "", "", str(date_value)
            else:
                # Для объектов datetime
                return date_value.strftime('%d'), date_value.strftime('%m'), date_value.strftime('%Y')
        except Exception as e:
            # Логируем ошибку для отладки
            logger.error(f"Ошибка при разборе даты {date_value}: {str(e)}")
            return "", "", ""

    def _to_roman(self, number):
        """Преобразует арабское число в римское"""
        try:
            num = int(number)
            roman_map = {2: "II", 3: "III", 4: "IV", 5: "V"}
            return roman_map.get(num, str(number))
        except (ValueError, TypeError):
            return str(number)

    def _save_image(self, img, output_filename, temp_png):
        """Сохраняет изображение в файл"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = self.output_dir / f"{output_filename}_{timestamp}.jpg"
        
        try:
            img.save(str(output_path), quality=95)
            logger.info(f"Изображение сохранено в {output_path}")
            
            # Удаляем временный файл PNG
            if temp_png and os.path.exists(temp_png):
                os.remove(temp_png)
                
            return output_path
        except Exception as save_error:
            logger.error(f"Ошибка сохранения изображения: {save_error}", exc_info=True)
            try:
                png_path = self.output_dir / f"{output_filename}_{timestamp}.png"
                img.save(str(png_path))
                logger.info(f"Изображение сохранено в формате PNG: {png_path}")
                return png_path
            except Exception:
                return None

    def _draw_coordinate_grid(self, img, scale_factor, grid_density):
        """Рисует координатную сетку для отладки"""
        # Создаем полупрозрачный слой для сетки
        grid_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        grid_draw = ImageDraw.Draw(grid_layer)
        
        # Настройки сетки
        grid_color = (180, 180, 180, 80)  # Полупрозрачный серый
        label_color = (70, 70, 70)        # Темно-серый для подписей
        small_font = ImageFont.truetype(str(self.font_path), 8)
        
        # Горизонтальные и вертикальные линии
        for x in range(0, img.width, grid_density):
            # Вертикальная линия
            grid_draw.line((x, 0, x, img.height), fill=grid_color, width=1)
            # Подпись координаты X
            real_x = int(x/scale_factor)
            grid_draw.text((x+2, 5), f"{real_x}", font=small_font, fill=label_color)
        
        for y in range(0, img.height, grid_density):
            # Горизонтальная линия
            grid_draw.line((0, y, img.width, y), fill=grid_color, width=1)
            # Подпись координаты Y
            real_y = int(y/scale_factor)
            grid_draw.text((5, y+2), f"{real_y}", font=small_font, fill=label_color)
        
        # Наложение сетки на изображение
        return Image.alpha_composite(img.convert('RGBA'), grid_layer).convert('RGB')

    def _place_text(self, draw, text, position, font, color=(0, 0, 0)):
        """
        Размещает текст на изображении в указанной позиции.
        
        Args:
            draw: Объект ImageDraw
            text: Текст для размещения
            position: Кортеж (x, y) координат
            font: Объект шрифта
            color: Цвет текста в формате RGB
        """
        if text and draw and font:
            draw.text(position, text, font=font, fill=color)
    
    def _place_centered_text(self, draw, text, position, width, font, color=(0, 0, 0)):
        """
        Размещает текст, центрированный по горизонтали в указанной области.
        
        Args:
            draw: Объект ImageDraw
            text: Текст для размещения
            position: Кортеж (x, y) где x - левая граница области, y - верхняя граница
            width: Ширина области, в которой нужно центрировать текст
            font: Объект шрифта
            color: Цвет текста в формате RGB
        """
        if text and draw and font:
            # Получаем размеры текста с указанным шрифтом
            text_width = font.getlength(text)
            
            # Расчет позиции для центрирования
            x_centered = position[0] + (width - text_width) / 2
            centered_position = (x_centered, position[1])
            
            # Отрисовка текста
            draw.text(centered_position, text, font=font, fill=color)

    def _place_multi_line_text(self, draw, text, position, max_width, font, color=(0, 0, 0), line_spacing=4):
        """
        Размещает многострочный текст с переносом по словам.
        
        Args:
            draw: Объект ImageDraw
            text: Текст для размещения
            position: Кортеж (x, y) координат начала текста
            max_width: Максимальная ширина строки
            font: Объект шрифта
            color: Цвет текста в формате RGB
            line_spacing: Отступ между строками в пикселях
        """
        if not text or not draw or not font:
            return
            
        words = text.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            # Проверяем, не превысит ли длина строки максимальную ширину
            test_line = current_line + " " + word
            test_width = font.getlength(test_line)
            
            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        # Добавляем последнюю строку
        lines.append(current_line)
        
        # Отрисовываем все строки
        y_position = position[1]
        for line in lines:
            draw.text((position[0], y_position), line, font=font, fill=color)
            y_position += font.getbbox(line)[3] + line_spacing

    def _save_to_database(self, data, protocol_number):
        try:
            self.db.execute('''INSERT INTO certificates 
                (protocol_number, fullname, workplace, position, group_number, 
                 cert_date, next_date, template_type, job_title)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (protocol_number,
                             data['fullname'],
                             data['workplace'],
                             data['position'],
                             str(data['qualification_group']),
                             data['cert_date'],
                             data['next_date'],
                             data.get('template_type', ''),
                             data['job_title']))
            self.db.commit()
        except Exception as e:
            logger.error(f"Ошибка сохранения в БД: {e}")
            # Продолжаем работу даже при ошибке БД
            pass
            
    def create_coordinate_grid(self, template_name='korotchka', grid_spacing=37, output_prefix="coord_grid", open_file=True):
        """
        Создает координатную сетку на основе выбранного шаблона.
        
        Args:
            template_name: Имя шаблона ('korotchka' для корочки электробезопасности)
            grid_spacing: Расстояние между линиями сетки в пикселях
            output_prefix: Префикс имени выходного файла
            open_file: Открыть файл после создания
            
        Returns:
            Path: Путь к созданному файлу с координатной сеткой
        """
        try:
            logger.info(f"Создание координатной сетки на основе шаблона {template_name} с шагом {grid_spacing}")
            
            # Определяем шаблон
            if template_name == 'korotchka':
                template_path = self.template_paths['Курс по электробезопасности']['korotchka']
            else:
                available_templates = list(self.template_paths.keys())
                logger.error(f"Шаблон '{template_name}' не найден. Доступные шаблоны: {available_templates}")
                return None
                
            # Открываем PDF файл и конвертируем в изображение
            pdf_document = pymupdf.open(str(template_path))
            page = pdf_document[0]
            zoom = 2  # zoom-фактор
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Сохраняем во временный файл
            temp_png = self.output_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pix.save(str(temp_png))
            
            # Открываем как PIL изображение
            img = Image.open(temp_png)
            pdf_document.close()
            
            # Записываем размеры
            width, height = img.width, img.height
            logger.info(f"Размер изображения: {width}x{height}")
            
            # Создаем объект для рисования
            draw = ImageDraw.Draw(img)
            scale_factor = zoom
            
            # Настройки сетки
            grid_color = (150, 150, 150)  # Серый цвет для линий
            label_color = (50, 50, 50)    # Темный серый для подписей
            
            # Рисуем горизонтальные линии
            for y in range(0, height, grid_spacing):
                draw.line((0, y, width, y), fill=grid_color, width=1)
                # Подписываем координаты
                real_y = int(y/scale_factor)
                draw.text((5, y+2), f"{real_y}", font=self.fonts['small'], fill=label_color)
            
            # Рисуем вертикальные линии
            for x in range(0, width, grid_spacing):
                draw.line((x, 0, x, height), fill=grid_color, width=1)
                # Подписываем координаты
                real_x = int(x/scale_factor)
                draw.text((x+2, 5), f"{real_x}", font=self.fonts['small'], fill=label_color)
            
            # Сохраняем результат
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"{output_prefix}_{template_name}_{grid_spacing}_{timestamp}.jpg"
            
            img.save(str(output_path), quality=95)
            logger.info(f"Координатная сетка сохранена в {output_path}")
            
            # Удаляем временный файл
            if os.path.exists(temp_png):
                os.remove(temp_png)
            
            # Открываем файл, если требуется
            if open_file:
                try:
                    logger.info("Открываю файл для просмотра...")
                    if platform.system() == 'Windows':
                        os.startfile(output_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', str(output_path)])
                    else:  # Linux
                        subprocess.call(['xdg-open', str(output_path)])
                except Exception as e:
                    logger.error(f"Ошибка при открытии файла: {e}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка создания координатной сетки: {e}", exc_info=True)
            return None
            
    def create_blank_grid(self, width=1684, height=1190, grid_spacing=37, output_prefix="blank_grid", open_file=True):
        """
        Создает пустую координатную сетку без шаблона.
        
        Args:
            width: Ширина изображения
            height: Высота изображения
            grid_spacing: Расстояние между линиями сетки в пикселях
            output_prefix: Префикс имени выходного файла
            open_file: Открыть файл после создания
            
        Returns:
            Path: Путь к созданному файлу с координатной сеткой
        """
        try:
            logger.info(f"Создание пустой координатной сетки размером {width}x{height} с шагом {grid_spacing}")
            
            # Создаем белый холст
            img = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Настройки сетки
            grid_color = (150, 150, 150)  # Серый цвет для линий
            label_color = (50, 50, 50)    # Темный серый для подписей
            
            # Рисуем горизонтальные линии
            for y in range(0, height, grid_spacing):
                draw.line((0, y, width, y), fill=grid_color, width=1)
                # Подписываем координаты
                draw.text((5, y+2), f"{y}", font=self.fonts['small'], fill=label_color)
            
            # Рисуем вертикальные линии
            for x in range(0, width, grid_spacing):
                draw.line((x, 0, x, height), fill=grid_color, width=1)
                # Подписываем координаты
                draw.text((x+2, 5), f"{x}", font=self.fonts['small'], fill=label_color)
            
            # Сохраняем результат
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"{output_prefix}_{grid_spacing}_{timestamp}.jpg"
            
            img.save(str(output_path), quality=95)
            logger.info(f"Пустая координатная сетка сохранена в {output_path}")
            
            # Открываем файл, если требуется
            if open_file:
                try:
                    logger.info("Открываю файл для просмотра...")
                    if platform.system() == 'Windows':
                        os.startfile(output_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', str(output_path)])
                    else:  # Linux
                        subprocess.call(['xdg-open', str(output_path)])
                except Exception as e:
                    logger.error(f"Ошибка при открытии файла: {e}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка создания пустой координатной сетки: {e}", exc_info=True)
            return None

    def create_detailed_grid(self, template_name='korotchka', grid_spacing=20, minor_grid_step=5, 
                           grid_opacity=70, show_labels=True, output_prefix="optimal_grid", open_file=True):
        """
        Создает детальную координатную сетку с улучшенной читаемостью.
        
        Args:
            template_name: Имя шаблона ('korotchka' для корочки электробезопасности)
            grid_spacing: Расстояние между основными линиями сетки в пикселях
            minor_grid_step: Расстояние между дополнительными линиями сетки в пикселях
            grid_opacity: Прозрачность сетки (0-255)
            show_labels: Показывать подписи координат
            output_prefix: Префикс имени выходного файла
            open_file: Открыть файл после создания
            
        Returns:
            Path: Путь к созданному файлу с координатной сеткой
        """
        try:
            logger.info(f"Создание детальной координатной сетки на основе шаблона {template_name}")
            logger.info(f"Параметры: основной шаг={grid_spacing}, дополнительный шаг={minor_grid_step}")
            
            # Определяем шаблон
            if template_name == 'korotchka':
                template_path = self.template_paths['Курс по электробезопасности']['korotchka']
            elif template_name == 'ohrana_truda':
                template_path = self.template_paths['Безопасность и Охрана труда']['korotchka']
            else:
                available_templates = ["korotchka", "ohrana_truda"]
                logger.error(f"Шаблон '{template_name}' не найден. Доступные шаблоны: {available_templates}")
                return None
                
            # Открываем PDF файл и конвертируем в изображение
            pdf_document = pymupdf.open(str(template_path))
            page = pdf_document[0]
            zoom = 2  # zoom-фактор
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Сохраняем во временный файл
            temp_png = self.output_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pix.save(str(temp_png))
            
            # Открываем как PIL изображение
            img = Image.open(temp_png)
            pdf_document.close()
            
            # Записываем размеры
            width, height = img.width, img.height
            logger.info(f"Размер изображения: {width}x{height}")
            
            # Создаем полупрозрачный слой для сетки
            grid_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            grid_draw = ImageDraw.Draw(grid_layer)
            
            scale_factor = zoom
            
            # Настройки сетки
            main_grid_color = (70, 70, 70, grid_opacity)     # Основные линии
            minor_grid_color = (150, 150, 150, grid_opacity // 2)  # Дополнительные линии
            axis_color = (0, 0, 150, grid_opacity + 50)      # Цвет осей
            label_color = (30, 30, 30)                       # Цвет подписей
            
            # Подготовка шрифтов для подписей
            small_font = ImageFont.truetype(str(self.font_path), 9)
            medium_font = ImageFont.truetype(str(self.font_path), 12)
            large_font = ImageFont.truetype(str(self.font_path), 16)
            
            # Рисуем дополнительные линии (более тонкие)
            if minor_grid_step > 0:
                # Горизонтальные дополнительные линии
                for y in range(0, height, minor_grid_step):
                    if y % grid_spacing != 0:  # Не основная линия
                        grid_draw.line((0, y, width, y), fill=minor_grid_color, width=1)
                
                # Вертикальные дополнительные линии
                for x in range(0, width, minor_grid_step):
                    if x % grid_spacing != 0:  # Не основная линия
                        grid_draw.line((x, 0, x, height), fill=minor_grid_color, width=1)
            
            # Рисуем основные линии
            # Горизонтальные основные линии
            for y in range(0, height, grid_spacing):
                grid_draw.line((0, y, width, y), fill=main_grid_color, width=1)
                # Подписываем координаты Y если нужно
                if show_labels:
                    real_y = int(y/scale_factor)
                    # Размещаем подпись слева
                    grid_draw.rectangle((2, y-8, 35, y+8), fill=(255, 255, 255, 200))
                    grid_draw.text((5, y-7), f"{real_y}", font=medium_font, fill=label_color)
            
            # Вертикальные основные линии
            for x in range(0, width, grid_spacing):
                grid_draw.line((x, 0, x, height), fill=main_grid_color, width=1)
                # Подписываем координаты X если нужно
                if show_labels:
                    real_x = int(x/scale_factor)
                    # Размещаем подпись сверху
                    grid_draw.rectangle((x-15, 2, x+15, 18), fill=(255, 255, 255, 200))
                    grid_draw.text((x-len(str(real_x))*3, 3), f"{real_x}", font=medium_font, fill=label_color)
            
            # Добавляем заголовок с информацией о сетке
            if show_labels:
                title = f"Координатная сетка (шаг {grid_spacing//scale_factor}px, масштаб {scale_factor}x)"
                title_bbox = large_font.getbbox(title)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (width - title_width) // 2
                
                # Фон для заголовка
                padding = 10
                grid_draw.rectangle(
                    (title_x - padding, 10 - padding, 
                     title_x + title_width + padding, 10 + title_bbox[3] + padding),
                    fill=(255, 255, 255, 220)
                )
                grid_draw.text((title_x, 10), title, font=large_font, fill=(0, 0, 0))
            
            # Накладываем сетку на изображение
            result_img = Image.alpha_composite(img.convert('RGBA'), grid_layer).convert('RGB')
            
            # Сохраняем результат
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"{output_prefix}_{template_name}_{grid_spacing}px_{timestamp}.jpg"
            
            result_img.save(str(output_path), quality=95)
            logger.info(f"Детальная координатная сетка сохранена в {output_path}")
            
            # Удаляем временный файл
            if os.path.exists(temp_png):
                os.remove(temp_png)
            
            # Открываем файл, если требуется
            if open_file:
                try:
                    logger.info("Открываю файл для просмотра...")
                    if platform.system() == 'Windows':
                        os.startfile(output_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', str(output_path)])
                    else:  # Linux
                        subprocess.call(['xdg-open', str(output_path)])
                except Exception as e:
                    logger.error(f"Ошибка при открытии файла: {e}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка создания детальной координатной сетки: {e}", exc_info=True)
            return None

    def generate_certificate(self, protocol_number, workplace, fullname, job_title, 
                          group, issue_date, inspection_date, reason="Первичная", 
                          assessment="Хорошо", next_inspection_date=None, debug_mode=False):
        """
        Генерирует сертификат (удостоверение) на основе переданных данных.
        
        Args:
            protocol_number: Номер протокола/удостоверения
            workplace: Организация
            fullname: ФИО
            job_title: Должность
            group: Группа допуска (II, III, IV, V)
            issue_date: Дата выдачи удостоверения
            inspection_date: Дата проверки
            reason: Причина проверки (по умолчанию "Первичная")
            assessment: Оценка (по умолчанию "Хорошо")
            next_inspection_date: Дата следующей проверки
            debug_mode: Включить режим отладки (показывать координатную сетку)
            
        Returns:
            Path: Путь к сгенерированному файлу сертификата
        """
        try:
            logger.info(f"Генерация сертификата для {fullname}")
            
            # Преобразуем группу в число, если это римская цифра
            group_num = self._roman_to_int(group) if isinstance(group, str) else group
            
            # Формируем данные для сертификата
            cert_data = {
                'protocol_number': protocol_number,
                'workplace': workplace,
                'fullname': fullname,
                'job_title': job_title,
                'group': str(group_num),
                'cert_date': issue_date,
                'next_date': next_inspection_date
            }
            
            # Путь к шаблону
            template_path = self.template_paths['Курс по электробезопасности']['korotchka']
            
            # Генерируем уникальное имя файла
            output_filename = f"{fullname.replace(' ', '_')}_cert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Создаем сертификат
            output_path = self._create_electrobez_korotchka(
                template_path=template_path,
                data=cert_data,
                output_filename=output_filename,
                debug_mode=debug_mode
            )
            
            if output_path:
                logger.info(f"Сертификат успешно создан: {output_path}")
                
                # Сохраняем в базу данных
                data_for_db = {
                    'fullname': fullname,
                    'workplace': workplace,
                    'job_title': job_title,
                    'position': 'Курс по электробезопасности',
                    'qualification_group': group_num,
                    'cert_date': issue_date,
                    'next_date': next_inspection_date,
                    'template_type': 'korotchka'
                }
                self._save_to_database(data_for_db, protocol_number)
                
                return output_path
            else:
                logger.error("Не удалось создать сертификат")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при генерации сертификата: {e}", exc_info=True)
            return None
            
    def _roman_to_int(self, roman):
        """Преобразует римское число в арабское"""
        roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        try:
            roman = roman.upper()
            total = 0
            i = 0
            
            while i < len(roman):
                # Если текущее значение меньше следующего, вычитаем его
                if i + 1 < len(roman) and roman_values[roman[i]] < roman_values[roman[i+1]]:
                    total += roman_values[roman[i+1]] - roman_values[roman[i]]
                    i += 2
                else:
                    total += roman_values[roman[i]]
                    i += 1
                    
            return total
        except (KeyError, TypeError):
            # Если не удалось преобразовать, возвращаем исходное значение или 0
            try:
                return int(roman)
            except (ValueError, TypeError):
                return 2  # По умолчанию группа II 

    def set_template_path(self, template_name):
        """
        Sets the template path based on the template name
        Args:
            template_name: Name of the template to use
        """
        template_paths = {
            'korotchka': Path('Электробез корочка .pdf'),  # Исправлено имя файла с пробелом перед .pdf
            'pozharnaya': Path('Пожарная безопастность корочка.pdf'),
            'prombez': Path('Промбез корочка.pdf'),
            'ohrana_truda': Path('Безопастность и охрана труда корочка.pdf')
        }
        
        if template_name not in template_paths:
            template_name = 'korotchka'
        
        self.template_path = template_paths[template_name]
        
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file {self.template_path} does not exist")
        
        return self.template_path 

def main():
    """
    Функция для тестовой генерации сертификата с заданными данными
    """
    # Создаем экземпляр генератора
    generator = ImageCertificateGenerator()
    
    # Выбор типа сертификата для тестирования
    cert_type = input("Выберите тип сертификата для тестирования (1 - Элбез, 2 - Охрана труда): ")
    debug_mode = True  # Включаем сетку для отладки
    
    if cert_type == "1":
        # Заполняем данные для сертификата электробезопасности
        protocol_number = "1234-ЭБ"
        workplace = "ООО \"ЭЛЕКТРОТЕХ\""
        fullname = "Петров Василий Иванович"
        job_title = "Инженер-электрик"
        group = "IV"
        issue_date = "15.04.2025"
        inspection_date = "15.04.2025"
        reason = "Первичная"
        assessment = "Хорошо"
        next_inspection_date = "15.04.2026"
        
        print("Генерация сертификата электробезопасности со следующими данными:")
        print(f"Номер: {protocol_number}")
        print(f"Организация: {workplace}")
        print(f"ФИО: {fullname}")
        print(f"Должность: {job_title}")
        print(f"Группа: {group}")
        print(f"Дата выдачи: {issue_date}")
        print(f"Дата проверки: {inspection_date}")
        print(f"Причина: {reason}")
        print(f"Оценка: {assessment}")
        print(f"Дата следующей проверки: {next_inspection_date}")
        
        # Генерируем удостоверение с заданными данными
        output_path = generator.generate_certificate(
            protocol_number=protocol_number,
            workplace=workplace,
            fullname=fullname,
            job_title=job_title,
            group=group,
            issue_date=issue_date,
            inspection_date=inspection_date,
            reason=reason,
            assessment=assessment,
            next_inspection_date=next_inspection_date,
            debug_mode=debug_mode  # Включаем сетку для проверки позиционирования
        )
    else:
        # Заполняем данные для сертификата охраны труда
        protocol_number = "1234-ОТ"
        workplace = "ООО \"БЕЗОПАСНОСТЬ\""
        fullname = "Смирнов Сергей Алексеевич"
        job_title = "Инженер по охране труда"
        issue_date = "15.04.2025"
        inspection_date = "15.04.2025"
        reason = "Первичная"
        assessment = "Хорошо"
        next_inspection_date = "15.04.2026"
        
        print("Генерация сертификата по охране труда со следующими данными:")
        print(f"Номер: {protocol_number}")
        print(f"Организация: {workplace}")
        print(f"ФИО: {fullname}")
        print(f"Должность: {job_title}")
        print(f"Дата выдачи: {issue_date}")
        print(f"Дата проверки: {inspection_date}")
        print(f"Причина: {reason}")
        print(f"Оценка: {assessment}")
        print(f"Дата следующей проверки: {next_inspection_date}")
        
        # Генерируем удостоверение по охране труда
        data = {
            'position': 'Безопасность и Охрана труда',
            'fullname': fullname,
            'workplace': workplace,
            'job_title': job_title,
            'qualification_group': '',  # Пустая строка для охраны труда
            'cert_date': issue_date,
            'next_date': next_inspection_date
        }
        
        success, files = generator.generate_document(data, debug_mode=debug_mode)
        output_path = files[0] if success and files else None
    
    if output_path:
        print(f"✅ Сертификат успешно создан: {output_path}")
        # Открываем сгенерированный файл
        if os.path.exists(output_path):
            if platform.system() == 'Windows':
                os.startfile(output_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', str(output_path)])
            else:  # Linux
                subprocess.call(['xdg-open', str(output_path)])
        else:
            print("❌ Ошибка: файл не найден")
    else:
        print("❌ Ошибка при генерации сертификата")
    
    # Создание тестовой координатной сетки
    print("\nСоздание тестовой координатной сетки...")
    grid_path = generator.create_detailed_grid(
        template_name='korotchka',
        grid_spacing=20,
        minor_grid_step=5,
        grid_opacity=80,
        show_labels=True
    )
    
    if grid_path:
        print(f"✅ Координатная сетка успешно создана: {grid_path}")
    else:
        print("❌ Ошибка при создании координатной сетки")

if __name__ == "__main__":
    main() 