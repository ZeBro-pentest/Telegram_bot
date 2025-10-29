from telebot import TeleBot
from config import BOT_TOKEN
from utils.storage import load_users
from handlers.start_handler import register_start_handlers
from handlers.thank_handler import register_thank_handlers
from handlers.cancel_handler import register_cancel_handlers
from handlers.admin_handler import register_admin_handlers
from handlers.common_handler import register_common_handlers
from handlers.cancel_action_handler import register_cancel_action_handler

bot = TeleBot(BOT_TOKEN, parse_mode="HTML")

# Загружаем пользователей
load_users()

# Регистрируем обработчики
register_start_handlers(bot)
register_thank_handlers(bot)
register_cancel_handlers(bot)
register_admin_handlers(bot)
register_common_handlers(bot)
register_cancel_action_handler(bot)

if __name__ == '__main__':
    print("✅ Бот запущен и готов принимать благодарения...")
    bot.polling(none_stop=True, skip_pending=True)
