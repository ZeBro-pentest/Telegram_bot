from utils.helpers import main_menu
from telebot import types

def register_common_handlers(bot):
    # Блокируем все не-текстовые сообщения
    @bot.message_handler(content_types=['photo','video','audio','voice','sticker','document','location','contact','video_note','animation'])
    def handle_non_text(message):
        bot.send_message(message.chat.id, '⚠️ Пожалуйста, отправь только текстовое сообщение 🙏', reply_markup=main_menu())

    @bot.message_handler(func=lambda m: m.text == 'ℹ️ О боте')
    def about(message):
        bot.send_message(message.chat.id, """ℹ️ Этот бот создан церковью <b>Слово Жизни Караганда</b>
как «Сосуд хвалы» — место, где каждый может делиться благодарностью Богу. Ваши слова вдохновляют и укрепляют веру.
""", parse_mode='HTML', reply_markup=main_menu())

    @bot.message_handler(commands=['exit'])
    def exit_cmd(message):
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.send_message(message.chat.id, '❌ Действие отменено. Возвращаемся в главное меню.', reply_markup=main_menu())

    @bot.message_handler(func=lambda m: True)
    def unknown(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('/start'))
        bot.send_message(message.chat.id, 'Чтобы начать, нажмите /start 🙏', reply_markup=markup)
