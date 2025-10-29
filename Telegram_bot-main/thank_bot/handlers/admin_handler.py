import os
import json
import re
from config import ADMIN_ID, THANKS_FOLDER
from utils.helpers import main_menu
from utils.storage import user_ids

# Команда	            Назначение
# /stats	            Показать статистику (кол-во пользователей, благодарений, файлов)
# /clear	            Удалить все файлы с благодарениями
# /broadcast	        Сделать рассылку всем пользователям
# /delete_broadcast	    Удалить последнюю рассылку у всех пользователей
# /exit	                Отменить текущее действие (например, при наборе текста рассылки)


# 📁 Файл для хранения отправленных рассылок
BROADCAST_LOG = "broadcast_log.json"

def register_admin_handlers(bot):
    broadcast_messages = []

    # ==================== 📊 /stats ====================
    @bot.message_handler(commands=['stats'])
    def show_stats(message):
        if message.from_user.id != ADMIN_ID:
            return bot.send_message(message.chat.id, "⛔ У вас нет доступа к этой команде.")

        total_thanks = 0
        total_days = 0

        if os.path.exists(THANKS_FOLDER):
            for fn in os.listdir(THANKS_FOLDER):
                if not fn.endswith(".txt"):
                    continue

                path = os.path.join(THANKS_FOLDER, fn)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                except Exception:
                    continue

                # Разделяем по двум пустым строкам
                entries = [x.strip() for x in re.split(r"\n\s*\n", content) if x.strip()]
                if entries:
                    total_days += 1
                    total_thanks += len(entries)

        users_count = len(user_ids)

        bot.send_message(
            message.chat.id,
            f"📈 <b>Статистика бота</b>\n\n"
            f"💌 Благодарений: <b>{total_thanks}</b>\n"
            f"📅 Активных дней: <b>{total_days}</b>\n"
            f"👥 В общем пользователей: <b>{users_count}</b>",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # ==================== 🧹 /clear ====================
    @bot.message_handler(commands=['clear'])
    def clear_data(message):
        if message.from_user.id != ADMIN_ID:
            return bot.send_message(message.chat.id, "⛔ У вас нет доступа к этой команде.")

        if not os.path.exists(THANKS_FOLDER):
            return bot.send_message(message.chat.id, "ℹ️ Папка с благодарениями ещё не создана.")

        deleted = 0
        for fn in os.listdir(THANKS_FOLDER):
            if fn.startswith("thanks_") and fn.endswith(".txt"):
                try:
                    os.remove(os.path.join(THANKS_FOLDER, fn))
                    deleted += 1
                except Exception:
                    pass

        bot.send_message(
            message.chat.id,
            f"🧹 Все благодарения удалены ({deleted} файлов).",
            reply_markup=main_menu()
        )

    # ==================== 📢 /broadcast ====================
    @bot.message_handler(commands=['broadcast'])
    def broadcast(message):
        if message.from_user.id != ADMIN_ID:
            return bot.send_message(message.chat.id, "⛔ Нет доступа к этой команде.")
        bot.send_message(message.chat.id, "Введите текст рассылки (или /exit для отмены):")
        bot.register_next_step_handler(message, send_broadcast)

    def send_broadcast(message):
        if message.from_user.id != ADMIN_ID:
            return

        # Отмена рассылки
        if message.text and message.text.strip().lower() == "/exit":
            bot.send_message(message.chat.id, "❌ Рассылка отменена.", reply_markup=main_menu())
            return

        text = (message.text or "").strip()
        if not text:
            bot.send_message(message.chat.id, "⚠️ Сообщение не может быть пустым.")
            return

        sent = 0
        broadcast_messages.clear()

        for uid in list(user_ids):
            try:
                msg = bot.send_message(uid, f"📢 {text}")
                broadcast_messages.append({"user_id": uid, "message_id": msg.message_id})
                sent += 1
            except Exception:
                pass

        # 💾 Сохраняем все message_id для возможности удаления
        with open(BROADCAST_LOG, "w", encoding="utf-8") as f:
            json.dump(broadcast_messages, f, ensure_ascii=False, indent=2)

        bot.send_message(
            message.chat.id,
            f"✅ Рассылка завершена.\n📨 Отправлено: <b>{sent}</b> сообщений.",
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # ==================== 🗑️ /delete_broadcast ====================
    @bot.message_handler(commands=['delete_broadcast'])
    def delete_broadcast(message):
        if message.from_user.id != ADMIN_ID:
            return bot.send_message(message.chat.id, "⛔ Нет доступа к этой команде.")

        if not os.path.exists(BROADCAST_LOG):
            return bot.send_message(message.chat.id, "ℹ️ Нет сохранённых рассылок для удаления.")

        with open(BROADCAST_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)

        removed = 0
        for entry in data:
            try:
                bot.delete_message(entry["user_id"], entry["message_id"])
                removed += 1
            except Exception:
                pass

        os.remove(BROADCAST_LOG)
        bot.send_message(
            message.chat.id,
            f"🗑️ Удалено {removed} сообщений у пользователей.",
            reply_markup=main_menu()
        )

    # ==================== 🚫 /exit — отмена любого действия ====================
    @bot.message_handler(commands=['exit'])
    def cancel_action(message):
        if message.from_user.id != ADMIN_ID:
            return bot.send_message(message.chat.id, "⛔ У вас нет активных действий для отмены.")
        bot.send_message(message.chat.id, "❌ Действие отменено.", reply_markup=main_menu())
