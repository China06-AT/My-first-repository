from datetime import datetime

async def create_summary(context) -> str:
    """
    Creates a formatted summary of all data gathered during the conversation.
    
    Args:
        context: The conversation context with user data
        
    Returns:
        str: A formatted summary string
    """
    # Создаем заголовок
    summary = "╔══════════════════════════╗\n"
    summary += "║    ВЫДАЧА УДОСТОВЕРЕНИЙ    ║\n"
    summary += "╚══════════════════════════╝\n\n"
    summary += "📋 Итоговая сводка:\n\n"

    # Для каждого человека
    for i in range(context.user_data['total_people']):
        # Создаем разделитель для каждого человека
        summary += "┌" + "─" * 40 + "┐\n"
        summary += f"│ 👤 Человек {i + 1}" + " " * (29 - len(str(i + 1))) + "│\n"
        summary += "├" + "─" * 40 + "┤\n"

        # Основная информация
        name_line = f"│ ФИО: {context.user_data['names'][i]}"
        summary += name_line + " " * (41 - len(name_line)) + "│\n"

        workplace_line = f"│ Организация: {context.user_data['workplaces'][i]}"
        summary += workplace_line + " " * (41 - len(workplace_line)) + "│\n"

        job_line = f"│ Должность: {context.user_data['job_titles'][i]}"
        summary += job_line + " " * (41 - len(job_line)) + "│\n"

        position_line = f"│ Курс: {context.user_data['positions'][i]}"
        summary += position_line + " " * (41 - len(position_line)) + "│\n"

        # Дополнительная информация для ПТМ
        if context.user_data['positions'][i] == 'Пожарная безопасность в объеме пожарно технического минимума':
            type_line = f"│ Тип: {context.user_data['fire_safety_types'][i]}"
            summary += type_line + " " * (41 - len(type_line)) + "│\n"

        # Информация о группе
        if context.user_data['positions'][i] == 'Курс по электробезопасности':
            group_line = f"│ Группа: {context.user_data['groups'][i]}"
            summary += group_line + " " * (41 - len(group_line)) + "│\n"
        elif context.user_data['positions'][i] == 'Безопасность и Охрана труда':
            check_type_line = f"│ Тип проверки: {context.user_data['check_types'][i]}"
            summary += check_type_line + " " * (41 - len(check_type_line)) + "│\n"

        # Даты
        cert_date = context.user_data['cert_dates'][i].strftime('%d.%m.%Y')
        date_line = f"│ Дата выдачи: {cert_date}"
        summary += date_line + " " * (41 - len(date_line)) + "│\n"

        if context.user_data['next_dates'][i]:
            next_date = context.user_data['next_dates'][i].strftime('%d.%m.%Y')
            next_date_line = f"│ Следующая проверка: {next_date}"
            summary += next_date_line + " " * (41 - len(next_date_line)) + "│\n"

        # Закрываем рамку для текущего человека
        summary += "└" + "─" * 40 + "┘\n\n"

    # Добавляем вопрос в конце
    summary += "Создать документы?"

    return summary


def validate_date(date_str: str) -> tuple:
    """
    Validates a date string in DD.MM.YYYY format.
    
    Args:
        date_str: String date in DD.MM.YYYY format
        
    Returns:
        tuple: (is_valid, datetime_obj or None, error_message or None)
    """
    try:
        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        
        # Check if date is in the future
        if date_obj > datetime.now():
            return False, None, "future_date"
            
        return True, date_obj, None
    except ValueError:
        return False, None, "invalid_format" 