from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import logging

from config import (PEOPLE_COUNT, FULLNAME, WORKPLACE, JOB_TITLE, POSITION,
                    GROUP, CHECK_TYPE, CERT_DATE, NEXT_DATE, CONFIRM_DATA,
                    POSITIONS, MESSAGES, COURSE_MAPPING, START_VARIATIONS)
from utils import create_summary
from certificate_generator import CertificateGenerator

# Настройка логирования
logger = logging.getLogger(__name__)

async def handle_start_variations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.lower()

    if message_text in START_VARIATIONS:
        context.user_data.clear()
        await update.message.reply_text(
            MESSAGES['start'],
            reply_markup=ReplyKeyboardRemove()
        )
        return PEOPLE_COUNT
    return ConversationHandler.END


async def get_people_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text.strip())
        if count <= 0:
            raise ValueError()

        context.user_data.clear()
        context.user_data.update({
            'total_people': count,
            'names': [],
            'workplaces': [],
            'job_titles': [],
            'positions': [],
            'groups': [],
            'cert_dates': [],
            'next_dates': [],
            'fire_safety_types': [],
            'check_types': []
        })

        if count == 1:
            await update.message.reply_text(
                "👤 Введите ФИО для 1 человека\n\n"
                "Пример:\n"
                "Иванов Андрей Андреевич"
            )
        else:
            await update.message.reply_text(
                MESSAGES['enter_names'].format(count) + "\n\n"
                                                        "Пример:\n" + "\n".join(
                    [f"Иванов Иван Иванович" for _ in range(min(count, 3))])
            )
        return FULLNAME

    except ValueError:
        await update.message.reply_text(MESSAGES['invalid_count'])
        return PEOPLE_COUNT


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    total_people = context.user_data['total_people']
    names = [name.strip() for name in text.split('\n') if name.strip()]

    if len(names) != total_people:
        if total_people == 1:
            await update.message.reply_text(
                "❌ Необходимо ввести ФИО для 1 человека\n\n"
                "Пример:\n"
                "Иванов Андрей Андреевич"
            )
        else:
            await update.message.reply_text(
                f"❌ Необходимо ввести {total_people} ФИО\n"
                f"Вы ввели {len(names)} ФИО\n\n"
                f"Введите {total_people} ФИО, каждое с новой строки:\n\n"
                "Пример:\n" + "\n".join([f"Иванов Иван Иванович" for _ in range(min(total_people, 3))])
            )
        return FULLNAME

    invalid_names = []
    for i, name in enumerate(names, 1):
        name_parts = name.split()
        if len(name_parts) < 2 or not all(part.replace('-', '').isalpha() for part in name_parts):
            invalid_names.append(f"{i}) {name}")

    if invalid_names:
        await update.message.reply_text(
            "❌ Следующие ФИО введены неверно:\n" +
            "\n".join(invalid_names) + "\n\n"
                                       "Требования к ФИО:\n"
                                       "- Минимум 2 слова\n"
                                       "- Только буквы и дефис\n"
                                       "- Каждое ФИО с новой строки\n\n"
                                       f"Введите все {total_people} ФИО заново"
        )
        return FULLNAME

    context.user_data['names'] = names
    await update.message.reply_text(
        f"🏢 Введите {'название организации' if total_people == 1 else 'названия организаций для ' + str(total_people) + ' человек'}\n\n"
        "Пример:\n" + "\n".join([f"ТОО \"Компания {i + 1}\"" for i in range(min(total_people, 3))])
    )
    return WORKPLACE


async def get_workplace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    total_people = context.user_data['total_people']
    workplaces = [wp.strip() for wp in text.split('\n') if wp.strip()]

    if len(workplaces) != total_people:
        await update.message.reply_text(
            f"❌ Необходимо ввести {total_people} {'организацию' if total_people == 1 else 'организаций'}\n"
            f"Вы ввели {len(workplaces)} {'организацию' if len(workplaces) == 1 else 'организаций'}\n\n"
            f"Введите {total_people} {'организацию' if total_people == 1 else 'организаций'}, "
            f"{'каждую ' if total_people > 1 else ''}с новой строки:\n\n"
            "Пример:\n" + "\n".join([f"ТОО \"Компания {i + 1}\"" for i in range(min(total_people, 3))])
        )
        return WORKPLACE

    context.user_data['workplaces'] = workplaces
    await update.message.reply_text(
        f"👔 Введите {'должность' if total_people == 1 else 'должности для ' + str(total_people) + ' человек'}:\n\n"
        "Пример:\n" + "\n".join(["Инженер-энергетик", "Электрик", "Начальник участка"][:min(total_people, 3)])
    )
    return JOB_TITLE


async def get_job_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    total_people = context.user_data['total_people']
    job_titles = [job.strip() for job in text.split('\n') if job.strip()]

    if len(job_titles) != total_people:
        if total_people == 1:
            await update.message.reply_text(
                "❌ Необходимо ввести должность\n\n"
                "Введите должность:\n\n"
                "Пример:\n"
                "Инженер-энергетик"
            )
        else:
            await update.message.reply_text(
                f"❌ Необходимо ввести {total_people} должностей\n"
                f"Вы ввели {len(job_titles)} должностей\n\n"
                f"Введите {total_people} должностей, каждую с новой строки:\n\n"
                "Пример:\n" + "\n".join(["Инженер-энергетик", "Электрик", "Начальник участка"][:min(total_people, 3)])
            )
        return JOB_TITLE

    context.user_data['job_titles'] = job_titles
    keyboard = [[pos] for pos in POSITIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        f"📚 Выберите курс обучения для {context.user_data['names'][len(context.user_data['positions'])]}:",
        reply_markup=reply_markup
    )
    return POSITION


async def get_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Инициализируем списки, если они еще не существуют
    if 'positions' not in context.user_data:
        context.user_data['positions'] = []
    if 'names' not in context.user_data:
        return ConversationHandler.END

    current_index = len(context.user_data['positions'])

    # Проверка на выход за пределы списка
    if current_index >= len(context.user_data['names']):
        await update.message.reply_text("❌ Произошла ошибка. Начните заново с команды /start")
        return ConversationHandler.END

    # Если это первый человек или предыдущий курс отличается
    if current_index == 0 or (current_index > 0 and context.user_data['positions'][-1] != text):
        selected_course = COURSE_MAPPING.get(text, text)
    else:
        # Автоматически используем тот же курс, что и для предыдущего человека
        selected_course = context.user_data['positions'][-1]

    if selected_course == 'Курс по электробезопасности':
        context.user_data['positions'].append(selected_course)
        keyboard = [['2', '3', '4', '5']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            f"Выберите группу допуска для {context.user_data['names'][current_index]}:",
            reply_markup=reply_markup
        )
        return GROUP

    elif selected_course == 'Пожарная безопасность в объеме пожарно технического минимума':
        context.user_data['positions'].append(selected_course)
        # Если предыдущий человек выбирал этот же курс, используем тот же тип
        if current_index > 0 and context.user_data['positions'][current_index - 1] == selected_course:
            prev_type = context.user_data['fire_safety_types'][-1]
            context.user_data['fire_safety_types'].append(prev_type)
            context.user_data['groups'].append('')

            if current_index + 1 < context.user_data['total_people']:
                # Спрашиваем, хочет ли пользователь использовать тот же курс для следующего человека
                keyboard = [
                    [f'✅ Тот же курс для {context.user_data["names"][current_index + 1]}'],
                    ['❌ Выбрать другой курс']
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                await update.message.reply_text(
                    f"Использовать курс «{selected_course}» ({prev_type}) для {context.user_data['names'][current_index + 1]}?",
                    reply_markup=reply_markup
                )
                return POSITION
            else:
                await update.message.reply_text(
                    "📅 Введите дату выдачи (дд.мм.гггг):\n"
                    "Например: 01.01.2024"
                )
                return CERT_DATE
        else:
            keyboard = [['1. Для ответственных'], ['2. Для работников']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f"Выберите тип обучения для {context.user_data['names'][current_index]}:",
                reply_markup=reply_markup
            )
            return GROUP

    elif selected_course == 'Безопасность и Охрана труда':
        context.user_data['positions'].append(selected_course)
        context.user_data['groups'].append('')
        # Если предыдущий человек выбирал этот же курс, используем тот же тип проверки
        if current_index > 0 and context.user_data['positions'][current_index - 1] == selected_course:
            prev_type = context.user_data['check_types'][-1]
            context.user_data['check_types'].append(prev_type)

            if current_index + 1 < context.user_data['total_people']:
                # Спрашиваем, хочет ли пользователь использовать тот же курс для следующего человека
                keyboard = [
                    [f'✅ Тот же курс для {context.user_data["names"][current_index + 1]}'],
                    ['❌ Выбрать другой курс']
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                await update.message.reply_text(
                    f"Использовать курс «{selected_course}» ({prev_type} проверка) для {context.user_data['names'][current_index + 1]}?",
                    reply_markup=reply_markup
                )
                return POSITION
            else:
                await update.message.reply_text(
                    "📅 Введите дату выдачи (дд.мм.гггг):\n"
                    "Например: 01.01.2024"
                )
                return CERT_DATE
        else:
            keyboard = [['первичный'], ['периодический']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f"Выберите тип проверки для {context.user_data['names'][current_index]}:",
                reply_markup=reply_markup
            )
            return CHECK_TYPE

    elif '✅ Тот же курс для' in text:
        # Автоматически используем тот же курс и настройки, что и для предыдущего человека
        prev_course = context.user_data['positions'][-1]
        context.user_data['positions'].append(prev_course)

        if prev_course == 'Пожарная безопасность в объеме пожарно технического минимума':
            prev_type = context.user_data['fire_safety_types'][-1]
            context.user_data['fire_safety_types'].append(prev_type)
            context.user_data['groups'].append('')
        elif prev_course == 'Безопасность и Охрана труда':
            prev_type = context.user_data['check_types'][-1]
            context.user_data['check_types'].append(prev_type)
            context.user_data['groups'].append('')
        elif prev_course == 'Курс по электробезопасности':
            prev_group = context.user_data['groups'][-1]
            context.user_data['groups'].append(prev_group)
        else:
            context.user_data['groups'].append('')

        if current_index + 1 < context.user_data['total_people']:
            # Спрашиваем про следующего человека
            keyboard = [
                [f'✅ Тот же курс для {context.user_data["names"][current_index + 1]}'],
                ['❌ Выбрать другой курс']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

            additional_info = ""
            if prev_course == 'Курс по электробезопасности':
                additional_info = f" (группа {prev_group})"
            elif prev_course == 'Пожарная безопасность в объеме пожарно технического минимума':
                additional_info = f" ({prev_type})"
            elif prev_course == 'Безопасность и Охрана труда':
                additional_info = f" ({prev_type} проверка)"

            await update.message.reply_text(
                f"Использовать курс «{prev_course}»{additional_info} для {context.user_data['names'][current_index + 1]}?",
                reply_markup=reply_markup
            )
            return POSITION
        else:
            await update.message.reply_text(
                "📅 Введите дату выдачи (дд.мм.гггг):\n"
                "Например: 01.01.2024"
            )
            return CERT_DATE

    elif '❌ Выбрать другой курс' in text:
        keyboard = [[pos] for pos in POSITIONS]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            f"📚 Выберите курс обучения для {context.user_data['names'][current_index]}:",
            reply_markup=reply_markup
        )
        return POSITION

    elif selected_course in COURSE_MAPPING.values():
        context.user_data['positions'].append(selected_course)
        context.user_data['groups'].append('')

        if current_index + 1 < context.user_data['total_people']:
            # Спрашиваем, хочет ли пользователь использовать тот же курс для следующего человека
            keyboard = [
                [f'✅ Тот же курс для {context.user_data["names"][current_index + 1]}'],
                ['❌ Выбрать другой курс']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f"Использовать курс «{selected_course}» для {context.user_data['names'][current_index + 1]}?",
                reply_markup=reply_markup
            )
            return POSITION
        else:
            await update.message.reply_text(
                "📅 Введите дату выдачи (дд.мм.гггг):\n"
                "Например: 01.01.2024"
            )
            return CERT_DATE
    else:
        keyboard = [[pos] for pos in POSITIONS]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "❌ Пожалуйста, выберите курс из списка",
            reply_markup=reply_markup
        )
        return POSITION


async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    current_index = len(context.user_data.get('groups', []))
    current_name = context.user_data['names'][current_index]
    position = context.user_data['positions'][current_index]

    if position == 'Курс по электробезопасности':
        try:
            group = int(text)
            if 2 <= group <= 5:
                if 'groups' not in context.user_data:
                    context.user_data['groups'] = []
                context.user_data['groups'].append(group)

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
                keyboard = [['2', '3', '4', '5']]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                await update.message.reply_text(
                    f"❌ Выберите группу допуска от 2 до 5 для {current_name}:",
                    reply_markup=reply_markup
                )
                return GROUP
        except ValueError:
            keyboard = [['2', '3', '4', '5']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f"❌ Выберите группу допуска от 2 до 5 для {current_name}:",
                reply_markup=reply_markup
            )
            return GROUP

    elif position == 'Пожарная безопасность в объеме пожарно технического минимума':
        if text.startswith('1.'):
            if 'fire_safety_types' not in context.user_data:
                context.user_data['fire_safety_types'] = []
            context.user_data['fire_safety_types'].append('Для ответственных')
            context.user_data.setdefault('groups', []).append('')
        elif text.startswith('2.'):
            if 'fire_safety_types' not in context.user_data:
                context.user_data['fire_safety_types'] = []
            context.user_data['fire_safety_types'].append('Для работников')
            context.user_data.setdefault('groups', []).append('')
        else:
            keyboard = [['1. Для ответственных'], ['2. Для работников']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text(
                f"❌ Выберите тип обучения для {current_name}:",
                reply_markup=reply_markup
            )
            return GROUP

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
        # Для остальных курсов
        context.user_data.setdefault('groups', []).append('')
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