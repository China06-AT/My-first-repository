# Состояния диалога
(PEOPLE_COUNT, FULLNAME, WORKPLACE, JOB_TITLE, POSITION,
 GROUP, CHECK_TYPE, CERT_DATE, NEXT_DATE, CONFIRM_DATA, CONFIRM_RESTART) = range(11)

# Доступные курсы
POSITIONS = [
    'Курс по электробезопасности',
    'Безопасность и Охрана труда',
    'Пожарная безопасность',
    'Промышленная безопасность'
]

# Опции для пожарной безопасности
FIRE_SAFETY_OPTIONS = [
    '1. Для ответственных',
    '2. Для работников'
]

# Варианты команды старт
START_VARIATIONS = [
    '/start', 'начать', 'старт', 'запуск', 'приступить', 'перейти к делу',
    'начать работу', 'начинаем', 'готов к началу', 'поехали', 'стартуем',
    'приступаем', 'давайте начнём', 'запустить', 'готов', 'начинаю',
    'перейти к задаче', 'перейти к сути', 'активировать', 'начало работы',
    'начнём', 'давайте приступим', 'хочу начать', 'давайте начинать',
    'готов к запуску', 'стартуем!', 'готов к работе', 'давайте начинать работу',
    'го', 'давай', 'создать', 'начало', 'старт!', 'поехали!', 'начинаем!',
    'СТАРТ', 'СТАРТУЕМ', 'СТАРТУЙТЕ', 'СТАРТУЙ'
]

# Шаблоны сообщений для многократного использования
MESSAGES = {
    'start': "👋 Здравствуйте!\n\nВведите количество человек для которых нужно сделать сертификат:",
    'invalid_count': "❌ Пожалуйста, введите положительное целое число",
    'enter_names': "👤 Введите ФИО для {} человек:\n(Введите каждое ФИО с новой строки)",
    'invalid_names': "❌ Следующие ФИО введены неверно:\n{}\n\nВведите все {} ФИО заново, каждое с новой строки",
    'enter_workplaces': "🏢 Введите названия организаций для {} человек:\n(Каждое с новой строки)",
    'enter_positions': "💼 Введите должности для {} человек:\n(Каждая с новой строки)",
    'choose_course': "📚 Выберите курс обучения для {}:",
    'enter_date': "📅 Введите дату выдачи удостоверения (дд.мм.гггг):\nПример: 01.02.2024",
    'invalid_date': "❌ Неверный формат даты.\n\nВведите дату в формате дд.мм.гггг\nПример: 01.02.2024",
    'future_date': "❌ Дата не может быть в будущем.\nВведите дату в формате дд.мм.гггг:",
    'confirm_data': "📋 Проверьте введенные данные:\n\n{}\nСоздать документы?",
    'generating': "⚙️ Начинаю генерацию документов...",
    'success': "✅ Готово! Для создания новых документов нажмите /start",
    'error': "❌ Произошла ошибка. Попробуйте снова: /start",
    'cancelled': "❌ Операция отменена. Для начала нажмите /start"
}

# Обновляем словарь соответствия курсов
COURSE_MAPPING = {
    'Курс по электробезопасности': 'Курс по электробезопасности',
    'Безопасность и Охрана труда': 'Безопасность и Охрана труда',
    'Пожарная безопасность': 'Пожарная безопасность в объеме пожарно технического минимума',
    'Промышленная безопасность': 'Промышленная безопасность РК по производству работ на опасных производственных объектах'
}

# Токен бота
BOT_TOKEN = "7661532547:AAE8wCPk_wi1OxE8jpTpqTS7Akd6pUWtu4Q" 