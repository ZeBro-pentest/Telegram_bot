import os
import re
import tempfile
from utils.helpers import main_menu
from config import THANKS_FOLDER

def register_cancel_handlers(bot):
    # ===== Вспомогательная функция =====
    def gather_user_entries(user_id):
        """Собирает все благодарения пользователя из всех файлов"""
        all_entries = []
        entries_map = []

        if not os.path.exists(THANKS_FOLDER):
            return all_entries, entries_map

        for fn in sorted(os.listdir(THANKS_FOLDER)):
            if not fn.startswith("thanks_") or not fn.endswith(".txt"):
                continue

            path = os.path.join(THANKS_FOLDER, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            parts = [x.strip() for x in re.split(r"\n\s*\n", content) if x.strip()]
            for p in parts:
                if re.search(rf"\(id\s*:\s*{user_id}\)", p):
                    all_entries.append(p)
                    entries_map.append((path, p))

        return all_entries, entries_map

    # ===== Обработка кнопки "🗑️ Удалить письмо" =====
    @bot.message_handler(func=lambda m: m.text == "🗑️ Удалить письмо")
    def show_user_thanks(message):
        user_id = message.from_user.id
        all_entries, _ = gather_user_entries(user_id)

        if not all_entries:
            return bot.send_message(
                message.chat.id,
                "❌ У вас пока нет сохранённых благодарений.",
                reply_markup=main_menu()
            )

        # Формируем список для пользователя
        response = ["📜 <b>Ваши благодарения:</b>\n"]
        for i, entry in enumerate(all_entries, start=1):
            # Берём только первую строку текста (или первые 80 символов)
            first_line = entry.split("\n", 1)[-1]
            short_text = (first_line[:80] + "…") if len(first_line) > 80 else first_line
            response.append(f"<b>{i}.</b> {short_text}")

        response.append("\nЧтобы удалить письмо, введите:\n<code>/cancel [номер]</code>\nНапример: /cancel 1")

        bot.send_message(
            message.chat.id,
            "\n".join(response),
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # ===== Обработка команды /cancel =====
    @bot.message_handler(commands=["cancel"])
    def cancel_thank(message):
        m = re.match(r"^/cancel(?:@\S+)?\s+(\d+)\s*$", message.text.strip() if message.text else "")
        if not m:
            return bot.send_message(
                message.chat.id,
                "⚠️ Используйте формат:\n<code>/cancel [номер]</code>\n\nПример: /cancel 1",
                parse_mode="HTML",
                reply_markup=main_menu()
            )

        index = int(m.group(1))
        user_id = message.from_user.id

        all_entries, entries_map = gather_user_entries(user_id)
        if not all_entries:
            return bot.send_message(
                message.chat.id,
                "❌ У вас пока нет сохранённых благодарений.",
                reply_markup=main_menu()
            )

        if index < 1 or index > len(all_entries):
            return bot.send_message(
                message.chat.id,
                f"⚠️ Неверный номер письма. У вас всего {len(all_entries)} благодарений.",
                reply_markup=main_menu()
            )

        # === Удаляем выбранное письмо ===
        target_file, target_entry = entries_map[index - 1]

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return bot.send_message(
                message.chat.id,
                "⚠️ Ошибка при чтении файла. Попробуйте позже.",
                reply_markup=main_menu()
            )

        parts = [x.strip() for x in re.split(r"\n\s*\n", content) if x.strip()]

        removed = False
        for i, p in enumerate(parts):
            if p == target_entry:
                del parts[i]
                removed = True
                break
        if not removed:
            for i, p in enumerate(parts):
                if target_entry in p or p in target_entry:
                    del parts[i]
                    removed = True
                    break

        if not removed:
            return bot.send_message(
                message.chat.id,
                "⚠️ Не удалось найти письмо для удаления.",
                reply_markup=main_menu()
            )

        # === Перезаписываем файл безопасно ===
        try:
            dirpath = os.path.dirname(target_file)
            fd, tmp_path = tempfile.mkstemp(prefix="tmp_", dir=dirpath, text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
                tmpf.write("\n\n".join(parts) + ("\n\n" if parts else ""))
            os.replace(tmp_path, target_file)
        except Exception:
            return bot.send_message(
                message.chat.id,
                "⚠️ Ошибка при записи файла.",
                reply_markup=main_menu()
            )

        bot.send_message(
            message.chat.id,
            f"✅ Ваше письмо №{index} успешно удалено.",
            reply_markup=main_menu()
        )
