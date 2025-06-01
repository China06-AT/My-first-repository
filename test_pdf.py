import sys
print(f"Python path: {sys.path}")
import pymupdf
print(f"PyMuPDF установлен: {pymupdf.__file__}")
import logging
from pathlib import Path
from PIL import Image
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pdf_conversion():
    try:
        # Путь к PDF файлу
        pdf_path = Path('Электробез корочка.pdf')
        
        if not pdf_path.exists():
            logger.error(f"PDF файл не найден: {pdf_path}")
            return False
            
        logger.info(f"PDF файл найден: {pdf_path}")
        
        # Создаем директорию для выходных файлов
        output_dir = Path('output_test')
        output_dir.mkdir(exist_ok=True)
        
        # Пробуем открыть PDF
        try:
            pdf_document = pymupdf.open(str(pdf_path))
            logger.info(f"PDF успешно открыт, количество страниц: {len(pdf_document)}")
            
            # Получаем первую страницу
            page = pdf_document[0]
            logger.info(f"Размеры страницы: {page.rect}")
            
            # Создаем изображение страницы
            zoom = 2.0
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            logger.info(f"Создано изображение размером: {pix.width}x{pix.height}")
            
            # Сохраняем во временный файл
            temp_path = output_dir / "temp.png"
            pix.save(str(temp_path))
            logger.info(f"Изображение сохранено в {temp_path}")
            
            # Открываем с помощью PIL
            img = Image.open(temp_path)
            logger.info(f"Изображение открыто через PIL: {img.size}")
            
            # Сохраняем JPEG для проверки
            jpg_path = output_dir / "output_test.jpg"
            img.save(str(jpg_path), quality=95)
            logger.info(f"Изображение сохранено как JPEG в {jpg_path}")
            
            # Закрываем PDF
            pdf_document.close()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке PDF: {e}", exc_info=True)
            return False
            
    except Exception as e:
        logger.error(f"Общая ошибка: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    result = test_pdf_conversion()
    print(f"Результат тестирования: {'УСПЕШНО' if result else 'ОШИБКА'}") 