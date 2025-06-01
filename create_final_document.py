from image_certificate_generator import ImageCertificateGenerator

# Точные координаты для документа (шаг 10 пикселей для максимальной точности)
PRECISE_COORDINATES = {
    'LEFT': {
        'protocol_number': (410, 304),
        'workplace': (220, 342),
        'fullname': (220, 373),
        'job_title': (220, 420),
        'group_text': (260, 620),
        'cert_day': (265, 530),
        'cert_month': (290, 530),
        'cert_year': (400, 530)
    },
    'RIGHT': {
        'cert_date': (735, 420),
        'reason': (805, 420),
        'group': (875, 420),
        'mark': (945, 420),
        'next_date': (1015, 420)
    }
}

def create_final_document():
    """
    Создает окончательный документ с точными координатами
    """
    # Создаем экземпляр генератора
    gen = ImageCertificateGenerator(template_name='korotchka')
    
    # Обновляем координаты на более точные
    gen.COORDINATES = PRECISE_COORDINATES
    
    # Тестовые данные
    test_data = {
        'protocol_number': '123',
        'workplace': 'ТОО Тест',
        'fullname': 'Иванов Иван Иванович',
        'job_title': 'Инженер-электрик',
        'group': '3',
        'cert_date': '15.04.2025',
        'next_date': '15.04.2026'
    }
    
    # Генерируем финальный документ без сетки
    final_document = gen.generate_certificate(
        **test_data,
        output_filename='final_precise_document',
        debug=False
    )
    print(f"Финальный документ создан: {final_document}")
    
    # Генерируем документ с сеткой для проверки
    document_with_grid = gen.generate_certificate(
        **test_data,
        output_filename='final_document_with_grid',
        debug=True,
        grid_density=50
    )
    print(f"Документ с сеткой для проверки создан: {document_with_grid}")
    
    # Открываем документы для просмотра
    import os
    os.startfile(final_document)
    os.startfile(document_with_grid)

if __name__ == "__main__":
    create_final_document() 