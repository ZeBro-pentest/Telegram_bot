import time
from datetime import datetime
from telebot import types
from utils.helpers import main_menu, thank_menu, is_thank_message
from utils.storage import save_thank, save_user

# 🧠 Память пользователя
user_attempts = {}
last_messages = {}

def register_thank_handlers(bot):
    @bot.message_handler(commands=['thank'])
    def thank_cmd(message):
        ask_for_thank(message)

    @bot.message_handler(func=lambda m: m.text == "✍️ Написать благодарность")
    def ask_for_thank(message):
        # Сохраняем пользователя
        save_user(message.from_user.id)

        # Отправляем инструкцию и включаем режим ожидания текста
        bot.send_message(
            message.chat.id,
            """📜 <b>Примерный формат письма благодарения:</b>

Ваш текст благодарения:
—---------------------------------------------------------------

ФИО (по желанию можно оставить анонимно)
✏️ Минимум 10 символов, максимум 400

Когда будете готовы — просто отправьте ваш текст в ответ на это сообщение.
Чтобы отменить — напишите /exit или нажмите «🚫 Отменить».
""",
            parse_mode='HTML',
            reply_markup=thank_menu()
        )
        bot.register_next_step_handler(message, save_message)

    def save_message(message):
        user_id = message.from_user.id

        # 🚫 Проверяем отмену
        if message.text and message.text.strip().lower() in ["/exit", "🚫 отменить"]:
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            bot.send_message(
                message.chat.id,
                "❌ Ввод отменён. Возвращаемся в главное меню.",
                reply_markup=main_menu()
            )
            return

        # ⚠️ Только текст
        if not message.text:
            bot.send_message(
                message.chat.id,
                "⚠️ Пожалуйста, отправь только текстовое сообщение 🙏",
                reply_markup=thank_menu()
            )
            return bot.register_next_step_handler(message, save_message)

        text = message.text.strip()
        length = len(text)

        # 📏 Проверка длины
        if length < 10:
            bot.send_message(
                message.chat.id,
                f"⚠️ Слишком коротко ({length}/10). Пожалуйста, опиши благодарение подробнее 🙏",
                reply_markup=thank_menu()
            )
            return bot.register_next_step_handler(message, save_message)

        if length > 400:
            bot.send_message(
                message.chat.id,
                f"⚠️ Слишком длинное сообщение ({length}/400). "
                "Сократи его, пожалуйста 🙏",
                reply_markup=thank_menu()
            )
            return bot.register_next_step_handler(message, save_message)

        # 🧠 Проверка смысла
        if not is_thank_message(text):
            user_attempts[user_id] = user_attempts.get(user_id, 0) + 1
            attempts = user_attempts[user_id]
            if attempts >= 3:
                bot.send_message(
                    message.chat.id,
                    "Похоже, вам сложно сейчас сформулировать благодарение.\n"
                    "Давайте начнём сначала ❤️",
                    reply_markup=main_menu()
                )
                user_attempts[user_id] = 0
                return
            else:
                bot.send_message(
                    message.chat.id,
                    f"⚠️ Это не похоже на благодарение.\n"
                    f"Попробуй ещё раз 🙏 (Попытка {attempts}/3)",
                    reply_markup=thank_menu()
                )
                return bot.register_next_step_handler(message, save_message)

        # 🕒 Проверка на частоту и дубликаты
        now = time.time()
        if user_id in last_messages:
            last_text = last_messages[user_id]['text']
            last_time = last_messages[user_id]['time']

            if text == last_text:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Вы уже отправляли это же благодарение. "
                    "Попробуй немного изменить текст 🙏",
                    reply_markup=thank_menu()
                )
                return bot.register_next_step_handler(message, save_message)

            if now - last_time < 30:
                remaining = int(30 - (now - last_time))
                bot.send_message(
                    message.chat.id,
                    f"⏳ Подожди ещё {remaining} секунд перед следующей отправкой 🙏",
                    reply_markup=thank_menu()
                )
                return bot.register_next_step_handler(message, save_message)

        # 💾 Сохраняем благодарение
        save_thank(user_id, message.from_user.full_name or 'Аноним', text)
        last_messages[user_id] = {'text': text, 'time': now}
        user_attempts[user_id] = 0

        # ✅ Подтверждение
        bot.send_message(
            message.chat.id,
            f"💌 Спасибо! Ваше благодарение сохранено и станет свидетельством Божьей славы ✝️\n"
            f"📏 Длина: {length}/400 символов.",
            reply_markup=main_menu()
        )
