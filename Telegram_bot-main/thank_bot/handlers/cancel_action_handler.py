from utils.helpers import main_menu

def register_cancel_action_handler(bot):
    @bot.message_handler(commands=['отменить'])
    @bot.message_handler(func=lambda m: m.text == "🚫 Отменить")
    def cancel_action(message):
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.send_message(
            message.chat.id,
            "❌ Действие отменено. Возвращаемся в главное меню.",
            reply_markup=main_menu()
        )

    # Также можно обрабатывать кнопку "Отменить"
    @bot.message_handler(func=lambda m: m.text and m.text.lower() in ["отменить", "❌ отменить", "🚫 отменить"])
    def cancel_button(message):
        """Позволяет отменить действием по кнопке"""
        try:
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        except Exception:
            pass

        bot.send_message(
            message.chat.id,
            "🚫 Текущее действие отменено.",
            reply_markup=main_menu()
        )
