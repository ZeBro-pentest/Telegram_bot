from telebot import types
import re

# 🏠 Главное меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("✍️ Написать благодарность")
    btn2 = types.KeyboardButton("🗑️ Удалить письмо")
    btn3 = types.KeyboardButton("ℹ️ О боте")
    markup.row(btn1)
    markup.row(btn2, btn3)
    return markup


# 📝 Клавиатура при вводе благодарения
def thank_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_cancel = types.KeyboardButton("🚫 Отменить")
    markup.row(btn_cancel)
    return markup


# 🧠 Проверка, является ли текст благодарением
def is_thank_message(text: str) -> bool:
    text = text.strip().lower()

    if len(text) < 10:
        return False
    if re.fullmatch(r'[\W\d_]+', text):  # только символы/цифры/эмодзи
        return False
    if "http" in text or "www" in text:
        return False

    spiritual_words = [
        "бог", "господ", "иисус", "дух", "молитв", "церковь",
        "вера", "чудо", "спас", "благослов", "слово жизни"
    ]
    gratitude_words = [
        "спасибо", "благодар", "признател", "слава", "хвала",
        "восхвал", "благодарен", "благодарю", "благодарность"
    ]

    has_spiritual = any(word in text for word in spiritual_words)
    has_gratitude = any(word in text for word in gratitude_words)

    return has_gratitude and has_spiritual
