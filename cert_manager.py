import logging
from certificate_generator import CertificateGenerator
from image_certificate_generator import ImageCertificateGenerator

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

class CertificateManager:
    """
    Менеджер сертификатов, управляющий различными типами генераторов.
    Автоматически выбирает нужный генератор в зависимости от типа сертификата.
    """
    
    def __init__(self):
        # Инициализируем оба генератора
        self.doc_generator = CertificateGenerator()
        self.image_generator = ImageCertificateGenerator()
        logger.info("Инициализированы генераторы сертификатов")
        
    def generate_documents(self, data):
        """
        Генерирует комплект документов для пользователя, включая все типы (docx и корочки)
        
        Args:
            data: Словарь с данными пользователя
            
        Returns:
            tuple: (success, list_of_file_paths)
        """
        generated_files = []
        success = True
        
        try:
            # Генерируем обычные документы Word
            doc_success, doc_files = self.doc_generator.generate_document(data)
            if doc_success and doc_files:
                generated_files.extend(doc_files)
                logger.info(f"Сгенерированы стандартные документы: {len(doc_files)} файлов")
            else:
                logger.warning("Не удалось сгенерировать стандартные документы")
                success = False
                
            # Генерируем корочку если это Курс по электробезопасности или Безопасность и Охрана труда
            if data['position'] in ['Курс по электробезопасности', 'Безопасность и Охрана труда']:
                img_success, img_files = self.image_generator.generate_document(data)
                if img_success and img_files:
                    generated_files.extend(img_files)
                    logger.info(f"Сгенерирована корочка для курса {data['position']}")
                else:
                    logger.warning(f"Не удалось сгенерировать корочку для курса {data['position']}")
                    # Не меняем общий статус успеха, так как корочка - дополнительный документ
            
            return success, generated_files
            
        except Exception as e:
            logger.error(f"Ошибка при генерации документов: {e}")
            return False, generated_files 