from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import logging

from config import (PEOPLE_COUNT, FULLNAME, WORKPLACE, JOB_TITLE, POSITION,
                    GROUP, CHECK_TYPE, CERT_DATE, NEXT_DATE, CONFIRM_DATA,
                    POSITIONS, MESSAGES)
from utils import create_summary
from cert_manager import CertificateManager

# Настройка логирования
logger = logging.getLogger(__name__)

async def get_check_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    current_index = len(context.user_data.get('check_types', []))
    current_name = context.user_data['names'][current_index]

    if text in ['первичный', 'периодический']:
        if 'check_types' not in context.user_data:
            context.user_data['check_types'] = []
        context.user_data['check_types'].append(text)

        # Если есть ещё люди
        if current_index + 1 < context.user_data['total_people']:
            keyboard = [[pos] for pos in POSITIONS]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f"Выберите курс для {context.user_data['names'][current_index + 1]}:",
                reply_markup=reply_markup
            )
            return POSITION
        else:
            await update.message.reply_text(
                "Введите дату выдачи (дд.мм.гггг):\n"
                "Например: 01.01.2024"
            )
            return CERT_DATE
    else:
        keyboard = [['первичный'], ['периодический']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            f"❌ Выберите тип проверки для {current_name}:",
            reply_markup=reply_markup
        )
        return CHECK_TYPE


async def get_cert_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if 'total_people' not in context.user_data:
            logger.error("total_people отсутствует в контексте")
            await update.message.reply_text(
                "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
            )
            return ConversationHandler.END

        # Инициализация списков, если их нет
        if 'next_dates' not in context.user_data:
            context.user_data['next_dates'] = [None] * context.user_data['total_people']
        if 'cert_dates' not in context.user_data:
            context.user_data['cert_dates'] = []

        text = update.message.text.strip()
        total_people = context.user_data['total_people']

        # Если это первый вызов функции
        if not text or text in ['/start', 'создать', '✅ Создать сертификаты', '❌ Начать заново'] or any(
                pos in text for pos in POSITIONS):
            message = f"📅 Введите дату выдачи (дд.мм.гггг) для {total_people} {'человека' if 2 <= total_people % 10 <= 4 and (total_people < 10 or total_people > 20) else 'человек'}:\n\n"

            # Проверяем наличие всех необходимых данных
            if 'names' not in context.user_data or 'positions' not in context.user_data:
                logger.error("Отсутствуют необходимые данные: names или positions")
                await update.message.reply_text(
                    "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
                )
                return ConversationHandler.END
                
            # Проверка на достаточное количество элементов
            if len(context.user_data['names']) < total_people or len(context.user_data['positions']) < total_people:
                logger.error(f"Недостаточно элементов: names={len(context.user_data['names'])}, positions={len(context.user_data['positions'])}, total_people={total_people}")
                await update.message.reply_text(
                    "❌ Произошла ошибка с данными. Пожалуйста, начните заново с команды /start"
                )
                return ConversationHandler.END

            # Добавляем информацию о каждом человеке
            for idx, name in enumerate(context.user_data['names'], 1):
                if idx > total_people:
                    break
                    
                try:
                    position = context.user_data['positions'][idx - 1]
                    message += f"{idx}) {name}\n"
                    message += f"    Курс: {position}\n"
                    if position == 'Курс по электробезопасности' and 'groups' in context.user_data and idx - 1 < len(context.user_data['groups']):
                        group = context.user_data['groups'][idx - 1]
                        message += f"    Группа: {group}\n"
                    message += "\n"
                except IndexError as e:
                    logger.error(f"Ошибка индексации при формировании сообщения: {e}")
                    continue  # Продолжаем с другими записями

            message += "Пример ввода дат:\n"
            example_dates = []
            for _ in range(total_people):
                example_dates.append("03.12.2024")
            message += "\n".join(example_dates)
            await update.message.reply_text(message)
            return CERT_DATE

        dates = [date.strip() for date in text.split('\n') if date.strip()]

        # Проверяем количество дат
        if len(dates) != total_people:
            message = f"❌ Необходимо ввести {total_people} {'дату' if total_people == 1 else 'даты' if 2 <= total_people % 10 <= 4 and (total_people < 10 or total_people > 20) else 'дат'}\n\n"
            message += f"📅 Введите дату выдачи (дд.мм.гггг) для {total_people} {'человека' if 2 <= total_people % 10 <= 4 and (total_people < 10 or total_people > 20) else 'человек'}:\n\n"

            # Добавляем информацию о каждом человеке
            for idx, name in enumerate(context.user_data['names'], 1):
                if idx > total_people:
                    break
                
                try:
                    position = context.user_data['positions'][idx - 1]
                    message += f"{idx}) {name}\n"
                    message += f"    Курс: {position}\n"
                    if position == 'Курс по электробезопасности' and 'groups' in context.user_data and idx - 1 < len(context.user_data['groups']):
                        group = context.user_data['groups'][idx - 1]
                        message += f"    Группа: {group}\n"
                    message += "\n"
                except IndexError as e:
                    logger.error(f"Ошибка индексации при формировании сообщения: {e}")
                    continue

            message += "Пример ввода дат:\n"
            example_dates = []
            for _ in range(total_people):
                example_dates.append("03.12.2024")
            message += "\n".join(example_dates)
            await update.message.reply_text(message)
            return CERT_DATE

        # Проверяем форматы дат
        cert_dates = []
        try:
            for i, date_str in enumerate(dates):
                try:
                    cert_date = datetime.strptime(date_str, '%d.%m.%Y')
                    if cert_date > datetime.now():
                        message = "❌ Дата не может быть в будущем\n\n"
                        message += f"📅 Введите дату выдачи (дд.мм.гггг) для {total_people} {'человека' if 2 <= total_people % 10 <= 4 and (total_people < 10 or total_people > 20) else 'человек'}:\n\n"

                        # Добавляем информацию о каждом человеке
                        for idx, name in enumerate(context.user_data['names'], 1):
                            if idx > total_people:
                                break
                                
                            try:
                                position = context.user_data['positions'][idx - 1]
                                message += f"{idx}) {name}\n"
                                message += f"    Курс: {position}\n"
                                if position == 'Курс по электробезопасности' and 'groups' in context.user_data and idx - 1 < len(context.user_data['groups']):
                                    group = context.user_data['groups'][idx - 1]
                                    message += f"    Группа: {group}\n"
                                message += "\n"
                            except IndexError:
                                continue

                        message += "Пример ввода дат:\n"
                        message += "\n".join(["01.01.2024" for _ in range(total_people)])
                        await update.message.reply_text(message)
                        return CERT_DATE
                    cert_dates.append(cert_date)
                except ValueError as e:
                    logger.error(f"Неверный формат даты #{i+1} '{date_str}': {str(e)}")
                    raise ValueError(f"Неверный формат даты '{date_str}'")
        except ValueError as e:
            message = f"❌ {str(e)}\n\n"
            message += f"📅 Введите дату выдачи (дд.мм.гггг) для {total_people} {'человека' if 2 <= total_people % 10 <= 4 and (total_people < 10 or total_people > 20) else 'человек'}:\n\n"

            # Добавляем информацию о каждом человеке
            for idx, name in enumerate(context.user_data['names'], 1):
                if idx > total_people:
                    break
                    
                try:
                    position = context.user_data['positions'][idx - 1]
                    message += f"{idx}) {name}\n"
                    message += f"    Курс: {position}\n"
                    if position == 'Курс по электробезопасности' and 'groups' in context.user_data and idx - 1 < len(context.user_data['groups']):
                        group = context.user_data['groups'][idx - 1]
                        message += f"    Группа: {group}\n"
                    message += "\n"
                except IndexError:
                    continue

            message += "Пример ввода дат:\n"
            message += "\n".join(["01.01.2024" for _ in range(total_people)])
            await update.message.reply_text(message)
            return CERT_DATE

        context.user_data['cert_dates'] = cert_dates

        # Определяем, для кого нужны следующие даты
        needs_next_dates = []
        for i, pos in enumerate(context.user_data['positions']):
            if i < len(cert_dates) and pos in ['Курс по электробезопасности', 'Пожарная безопасность в объеме пожарно технического минимума']:
                needs_next_dates.append(i)

        if needs_next_dates:
            message = f"📅 Введите дату следующей проверки (дд.мм.гггг) для {len(needs_next_dates)} {'человека' if 2 <= len(needs_next_dates) % 10 <= 4 and (len(needs_next_dates) < 10 or len(needs_next_dates) > 20) else 'человек'}:\n\n"

            # Добавляем информацию о каждом человеке
            for idx, i in enumerate(needs_next_dates, 1):
                try:
                    if i >= len(context.user_data['names']) or i >= len(context.user_data['positions']) or i >= len(cert_dates):
                        logger.error(f"Индекс {i} выходит за пределы списка names, positions или cert_dates")
                        continue
                        
                    name = context.user_data['names'][i]
                    position = context.user_data['positions'][i]
                    cert_date = cert_dates[i].strftime('%d.%m.%Y')

                    message += f"{idx}) {name}\n"
                    message += f"    Курс: {position}\n"
                    message += f"    Дата выдачи: {cert_date}\n"
                    if position == 'Курс по электробезопасности' and 'groups' in context.user_data and i < len(context.user_data['groups']):
                        group = context.user_data['groups'][i]
                        message += f"    Группа: {group}\n"
                    message += "\n"
                except IndexError as e:
                    logger.error(f"Ошибка индексации при формировании сообщения о следующих датах: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Другая ошибка при формировании сообщения о следующих датах: {e}")
                    continue

            message += "Пример ввода дат:\n"
            example_dates = []
            for _ in range(len(needs_next_dates)):
                example_dates.append("03.12.2025")
            message += "\n".join(example_dates)

            await update.message.reply_text(message)
            context.user_data['needs_next_dates'] = needs_next_dates
            return NEXT_DATE
        else:
            # Если нет необходимости в дополнительных датах
            context.user_data['next_dates'] = [None] * total_people
            return await show_summary(update, context)

    except Exception as e:
        logger.error(f"Ошибка обработки дат: {str(e)}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Введите даты заново"
        )
        return CERT_DATE


async def get_next_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        needs_next_dates = context.user_data.get('needs_next_dates', [])

        # Проверяем, есть ли needs_next_dates в контексте
        if not needs_next_dates:
            logger.error("needs_next_dates отсутствует в контексте")
            await update.message.reply_text(
                "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
            )
            return ConversationHandler.END

        # Если это первый вызов функции или текст содержит даты
        if all(str(i) in text for i in range(10)):  # Проверяем наличие цифр в тексте
            message = f"📅 Введите дату следующей проверки (дд.мм.гггг) для {len(needs_next_dates)} {'человека' if 2 <= len(needs_next_dates) % 10 <= 4 and (len(needs_next_dates) < 10 or len(needs_next_dates) > 20) else 'человек'}:\n\n"

            # Проверяем наличие всех необходимых данных
            required_keys = ['names', 'positions', 'cert_dates']
            if not all(key in context.user_data for key in required_keys):
                missing_keys = [key for key in required_keys if key not in context.user_data]
                logger.error(f"Отсутствуют необходимые данные в контексте: {missing_keys}")
                await update.message.reply_text(
                    "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
                )
                return ConversationHandler.END
                
            # Проверка на достаточное количество элементов в списках
            for key in required_keys:
                if len(context.user_data.get(key, [])) < max(needs_next_dates) + 1:
                    logger.error(f"Недостаточно элементов в {key}: {len(context.user_data.get(key, []))} < {max(needs_next_dates) + 1}")
                    await update.message.reply_text(
                        "❌ Произошла ошибка с данными. Пожалуйста, начните заново с команды /start"
                    )
                    return ConversationHandler.END

            # Добавляем информацию о каждом человеке
            for idx, i in enumerate(needs_next_dates, 1):
                try:
                    if i >= len(context.user_data['names']) or i >= len(context.user_data['positions']) or i >= len(context.user_data['cert_dates']):
                        logger.error(f"Индекс {i} выходит за пределы одного из списков")
                        continue
                        
                    name = context.user_data['names'][i]
                    position = context.user_data['positions'][i]
                    cert_date = context.user_data['cert_dates'][i].strftime('%d.%m.%Y')

                    message += f"{idx}) {name}\n"
                    message += f"    Курс: {position}\n"
                    message += f"    Дата выдачи: {cert_date}\n"
                    if position == 'Курс по электробезопасности' and 'groups' in context.user_data and i < len(context.user_data['groups']):
                        group = context.user_data['groups'][i]
                        message += f"    Группа: {group}\n"
                    message += "\n"
                except IndexError as e:
                    logger.error(f"Ошибка индексации при формировании сообщения: {e}")
                    continue  # Продолжаем с другими записями вместо прерывания
                except Exception as e:
                    logger.error(f"Другая ошибка при формировании сообщения: {e}")
                    continue

            message += "Пример ввода дат:\n"
            message += "\n".join(["03.12.2025" for _ in range(len(needs_next_dates))])

            await update.message.reply_text(message)
            return NEXT_DATE

        # Обработка введенных дат
        dates = [date.strip() for date in text.split('\n') if date.strip()]

        if len(dates) != len(needs_next_dates):
            message = f"❌ Необходимо ввести {len(needs_next_dates)} {'дату' if len(needs_next_dates) == 1 else 'даты' if 2 <= len(needs_next_dates) % 10 <= 4 and (len(needs_next_dates) < 10 or len(needs_next_dates) > 20) else 'дат'}\n\n"
            message += f"Введите даты заново:\n"
            message += "\n".join(["01.02.2024" for _ in range(len(needs_next_dates))])
            await update.message.reply_text(message)
            return NEXT_DATE

        # Инициализация списка следующих дат
        next_dates = [None] * context.user_data['total_people']
        invalid_dates = []

        # Проверка и обработка дат
        for i, date_str in enumerate(dates):
            try:
                if i >= len(needs_next_dates):
                    logger.error(f"Индекс {i} выходит за пределы списка needs_next_dates длиной {len(needs_next_dates)}")
                    continue
                    
                next_date = datetime.strptime(date_str, '%d.%m.%Y')
                person_index = needs_next_dates[i]

                if 'cert_dates' not in context.user_data or not context.user_data['cert_dates']:
                    logger.error("Список cert_dates отсутствует или пуст")
                    raise ValueError("Список cert_dates отсутствует или пуст")
                
                if person_index >= len(context.user_data['cert_dates']):
                    logger.error(f"Индекс {person_index} выходит за пределы списка cert_dates длиной {len(context.user_data['cert_dates'])}")
                    raise IndexError(f"Индекс {person_index} выходит за пределы списка cert_dates")

                cert_date = context.user_data['cert_dates'][person_index]
                
                if cert_date is None:
                    logger.error(f"cert_date для индекса {person_index} равен None")
                    raise ValueError(f"cert_date для индекса {person_index} равен None")

                if next_date <= cert_date:
                    if person_index >= len(context.user_data['names']):
                        logger.error(f"Индекс {person_index} выходит за пределы списка names")
                        raise IndexError(f"Индекс {person_index} выходит за пределы списка names")
                        
                    name = context.user_data['names'][person_index]
                    invalid_dates.append(
                        f"❌ {name}:\n"
                        f"    Дата следующей проверки ({next_date.strftime('%d.%m.%Y')})\n"
                        f"    должна быть позже даты выдачи ({cert_date.strftime('%d.%m.%Y')})"
                    )
                else:
                    next_dates[person_index] = next_date

            except (ValueError, IndexError) as e:
                logger.error(f"Ошибка при обработке даты ({i}, {date_str}): {str(e)}")
                await update.message.reply_text(
                    "❌ Произошла ошибка при обработке дат. Пожалуйста, введите даты заново в формате дд.мм.гггг"
                )
                return NEXT_DATE

        if invalid_dates:
            message = "❌ Обнаружены ошибки:\n\n"
            message += "\n\n".join(invalid_dates)
            message += "\n\nВведите все даты заново:\n"
            message += "\n".join(["01.02.2024" for _ in range(len(needs_next_dates))])
            await update.message.reply_text(message)
            return NEXT_DATE

        context.user_data['next_dates'] = next_dates
        return await show_summary(update, context)

    except Exception as e:
        logger.error(f"Ошибка обработки следующих дат: {str(e)}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, начните заново с команды /start"
        )
        return ConversationHandler.END


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    summary = await create_summary(context)
    keyboard = [['✅ Создать сертификаты', '❌ Начать заново']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        f"Проверьте данные:\n\n{summary}",
        reply_markup=reply_markup
    )
    return CONFIRM_DATA


async def confirm_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text.strip()

    if '✅' in response or 'да' in response.lower():
        # Создаем экземпляр менеджера сертификатов
        manager = CertificateManager()
        
        # Для каждого человека создаем отдельные сертификаты
        for i in range(context.user_data['total_people']):
            try:
                data = {
                    'fullname': context.user_data['names'][i],
                    'workplace': context.user_data['workplaces'][i],
                    'job_title': context.user_data['job_titles'][i],
                    'position': context.user_data['positions'][i],
                    'qualification_group': context.user_data.get('groups', [None] * context.user_data['total_people'])[i],
                    'cert_date': context.user_data.get('cert_dates', [None])[i],
                    'next_date': context.user_data.get('next_dates', [None])[i],
                    'template_type': ''
                }

                if data['position'] == 'Пожарная безопасность в объеме пожарно технического минимума':
                    data['template_type'] = context.user_data.get('fire_safety_types', [])[i]
                elif data['position'] == 'Безопасность и Охрана труда':
                    data['qualification_group'] = context.user_data.get('check_types', [])[i]

                success, file_paths = manager.generate_documents(data)

                if success and file_paths:
                    for file_path in file_paths:
                        try:
                            await update.message.reply_document(
                                document=open(file_path, 'rb'),
                                filename=file_path.name,
                                caption=f"✅ Сертификат для {data['fullname']} создан!"
                            )
                        except Exception as e:
                            logger.error(f"Ошибка отправки файла {file_path}: {e}")
                            await update.message.reply_text(
                                f"⚠️ Сертификат создан, но возникла ошибка при отправке: {file_path.name}"
                            )
                else:
                    await update.message.reply_text(
                        f"❌ Ошибка создания сертификата для {data['fullname']}"
                    )

            except Exception as e:
                logger.error(f"Ошибка генерации: {e}")
                await update.message.reply_text(
                    f"❌ Ошибка при создании сертификата для {context.user_data['names'][i]}"
                )
                continue

        await update.message.reply_text(MESSAGES['success'])
        return ConversationHandler.END

    elif '❌' in response or 'нет' in response:
        await update.message.reply_text(
            "🔄 Начинаем заново.\n\nВведите количество человек:",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return PEOPLE_COUNT

    else:
        keyboard = [['✅ Да, создать документы', '❌ Нет, начать заново']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "❌ Выберите один из вариантов:",
            reply_markup=reply_markup
        )
        return CONFIRM_DATA


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGES['cancelled'], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END 