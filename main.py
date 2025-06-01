import logging
import sys
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)

from config import (
    PEOPLE_COUNT, FULLNAME, WORKPLACE, JOB_TITLE, POSITION,
    GROUP, CHECK_TYPE, CERT_DATE, NEXT_DATE, CONFIRM_DATA,
    START_VARIATIONS, BOT_TOKEN
)

from bot_handlers import (
    handle_start_variations, get_people_count, get_name, get_workplace,
    get_job_title, get_position, get_group
)

from bot_handlers_part2 import (
    get_check_type, get_cert_date, get_next_date, show_summary,
    confirm_data, cancel
)

def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    try:
        # Создание и настройка приложения
        application = Application.builder().token(BOT_TOKEN).build()

        # Добавление обработчиков
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', handle_start_variations),
                MessageHandler(filters.Regex(f"^({'|'.join(START_VARIATIONS)})$"), handle_start_variations)
            ],
            states={
                PEOPLE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_people_count)],
                FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                WORKPLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_workplace)],
                JOB_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_job_title)],
                POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_position)],
                GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
                CERT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cert_date)],
                NEXT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_next_date)],
                CONFIRM_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_data)],
                CHECK_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_check_type)]
            },
            fallbacks=[
                CommandHandler('cancel', cancel),
                CommandHandler('start', handle_start_variations),
                MessageHandler(filters.Regex(f"^({'|'.join(START_VARIATIONS)})$"), handle_start_variations)
            ],
            allow_reentry=True
        )

        application.add_handler(conv_handler)

        # Запуск бота с параметрами для предотвращения конфликтов
        print("✅ Бот запущен и готов к работе!")
        print("ℹ️ Нажмите Ctrl+C для остановки")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=True
        )

    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {str(e)}")
        logging.error(f"Ошибка при запуске бота: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 