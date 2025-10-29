from utils.helpers import main_menu
from utils.storage import save_user

def register_start_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        save_user(user_id)
        bot.send_message(
            message.chat.id,
            """Здравствуйте 😊

Мы рады приветствовать вас в телеграм боте от церкви <b>Слово Жизни Караганда</b>!

Здесь вы можете написать письмо благодарности Богу 🙏
""",
            reply_markup=main_menu()
        )
