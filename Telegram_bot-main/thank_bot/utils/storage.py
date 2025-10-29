import os
from datetime import datetime
from config import USERS_FILE, THANKS_FOLDER

user_ids = set()

def load_users():
    global user_ids
    os.makedirs(os.path.dirname(USERS_FILE) or '.', exist_ok=True)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    user_ids.add(int(line))

def save_user(user_id: int):
    global user_ids
    os.makedirs(os.path.dirname(USERS_FILE) or '.', exist_ok=True)
    if user_id not in user_ids:
        with open(USERS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{user_id}\n")
        user_ids.add(user_id)

def save_thank(user_id: int, username: str, text: str):
    os.makedirs(THANKS_FOLDER, exist_ok=True)
    date = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    file_path = os.path.join(THANKS_FOLDER, f"thanks_{date}.txt")
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] (id:{user_id}) {username}:\n{text}\n\n")
