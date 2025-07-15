import sqlite3
import time
import random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import calendar

DATABASE_NAME = 'database.db'

def connect_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def initialize_database():
    conn = connect_db()
    cursor = conn.cursor()

    # Создание таблицы users
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT DEFAULT NULL,
                stars REAL DEFAULT 0.0,
                count_refs INTEGER DEFAULT 0,
                referral_id INTEGER DEFAULT NULL,
                withdrawn REAL DEFAULT 0.0,
                registration_time REAL DEFAULT (strftime('%s','now'))
            )
        ''')
        print('Таблица "users" создана')
    else:
        print('Выполнено подключение к таблице "users".')

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN registration_time REAL DEFAULT (strftime('%s','now'))")
        print('Поле registration_time добавлено в таблицу "users"')
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print('Выполнено подключение к полю registration_time в таблице "users".')
        else:
            print(f"Ошибка при добавлении поля registration_time: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
        print('Поле banned добавлено в таблицу "users"')
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print('Выполнено подключение к полю banned в таблице "users".')
        else:
            print(f"Ошибка при добавлении поля banned: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN count_tasker INTEGER DEFAULT 0")
        print('Поле count_tasker добавлено в таблицу "users"')
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print('Выполнено подключение к полю count_tasker в таблице "users".')
        else:
            print(f"Ошибка при добавлении поля count_tasker: {e}")

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="promocodes"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                id INTEGER PRIMARY KEY,
                code TEXT NOT NULL UNIQUE,
                stars REAL NOT NULL,
                max_uses INTEGER NOT NULL,
                current_uses INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        print('Таблица "promocodes" создана')
    else:
        print('Выполнено подключение к таблице "promocodes".')

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="promocode_uses"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocode_uses (
                id INTEGER PRIMARY KEY,
                promocode_id INTEGER,
                user_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (promocode_id) REFERENCES promocodes(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(promocode_id, user_id)
            )
        ''')
        print('Таблица "promocode_uses" создана')
    else:
        print('Выполнено подключение к таблице "promocode_uses".')
    
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="new_tasks"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS new_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                reward REAL NOT NULL,
                link TEXT DEFAULT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                bot TEXT DEFAULT 'None',
                max_completed INTEGER DEFAULT 0,
                current_completed INTEGER DEFAULT 0
            )
        ''')
        print('Таблица "new_tasks" создана')
    else:
        print('Выполнено подключение к таблице "new_tasks".')

    try:
        cursor.execute("ALTER TABLE new_tasks ADD COLUMN id_channel_private INTEGER DEFAULT 0")
        print('Поле id_channel_private добавлено в таблицу "new_tasks"')
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print('Выполнено подключение к полю id_channel_private в таблице "new_tasks".')
        else:
            print(f"Ошибка при добавлении поля id_channel_private: {e}")

    # Создание таблицы completed_tasks
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="completed_tasks"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, task_id)
            )
        ''')
        print('Таблица "completed_tasks" создана')
    else:
        print('Выполнено подключение к таблице "completed_tasks".')

    # Создание таблицы click_times
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="click_times"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS click_times (
                user_id INTEGER PRIMARY KEY,
                last_click_time REAL NOT NULL,
                click_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print('Таблица "click_times" создана')
    else:
        print('Выполнено подключение к таблице "click_times".')

    # Создание таблицы daily_gifts
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="daily_gifts"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_gifts (
                user_id INTEGER PRIMARY KEY,
                last_claimed_time REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print('Таблица "daily_gifts" создана')
    else:
        print('Выполнено подключение к таблице "daily_gifts".')
    
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="withdrawales"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS withdrawales (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                stars REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        print('Таблица "withdrawales" создана')
    else:
        print('Выполнено подключение к таблице "withdrawales".')
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="booster"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booster (
                id INTEGER PRIMARY KEY,
                username TEXT DEFAULT NULL,
                user_id INTEGER NOT NULL,
                end_time REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print('Таблица "booster" создана')
    else:
        print('Выполнено подключение к таблице "booster".')
    
    cursor.execute('PRAGMA table_info(booster)')
    columns = cursor.fetchall()
    username_column = next((col for col in columns if col[1] == 'username'), None)

    if username_column:
        if username_column[3] == 1:
            print('Столбец "username" имеет ограничение NOT NULL. Изменяем на DEFAULT NULL...')
            cursor.execute("""
                ALTER TABLE booster
                RENAME TO temp_booster
            """)
            cursor.execute("""
                CREATE TABLE booster (
                    id INTEGER PRIMARY KEY,
                    username TEXT DEFAULT NULL,
                    user_id INTEGER NOT NULL,
                    end_time REAL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                INSERT INTO booster (id, username, user_id, end_time)
                SELECT id, username, user_id, end_time FROM temp_booster
            """)
            cursor.execute("DROP TABLE temp_booster")
            print('Ограничение NOT NULL удалено, установлено DEFAULT NULL.')
        else:
            print('Столбец "username" уже имеет DEFAULT NULL.')
    else:
        print('Столбец "username" не найден в таблице "booster".')

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="lottery"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lottery (
                id INTEGER PRIMARY KEY,
                status TEXT NOT NULL,
                cash REAL NOT NULL,
                ticket_cash REAL NOT NULL,
                winner_id INTEGER DEFAULT NULL
            )
        """)
        print('Таблица "lottery" создана')
    else:
        print('Выполнено подключение к таблице "lottery".')

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="lottery_data"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lottery_data (
                lottery_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                count_tickets INTEGER DEFAULT 0,
                FOREIGN KEY (lottery_id) REFERENCES lottery(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print('Таблица "lottery_data" создана')
    else:
        print('Выполнено подключение к таблице "lottery_data".')

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="knb"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knb (
                id_game INTEGER PRIMARY KEY,
                first_player INTEGER NOT NULL,
                second_player INTEGER NOT NULL,
                choice_first TEXT DEFAULT NULL,
                choice_second TEXT DEFAULT NULL,
                result TEXT DEFAULT NULL,
                bet REAL NOT NULL,
                FOREIGN KEY (first_player) REFERENCES users(id),
                FOREIGN KEY (second_player) REFERENCES users(id)
            )
        """)
        print('Таблица "knb" создана')
    else:
        print('Выполнено подключение к таблице "knb".')
    
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="utm_data"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utm_data (
                url TEXT NOT NULL,
                count_users INTEGER DEFAULT 0,
                count_op_users INTEGER DEFAULT 0
            )
        """)
        print('Таблица "utm_data" создана')
    else:
        print('Выполнено подключение к таблице "utm_data".')

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="task_data"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_data (
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print('Таблица "task_data" создана')
    else:
        print('Выполнено подключение к таблице "task_data".')
    
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="flyer_task"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flyer_task (
                task_hash TEXT PRIMARY KEY
            )
        """)
        print('Таблица "flyer_task" создана')
    else:
        print('Выполнено подключение к таблице "flyer_task".')

    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="op_not_checker"').fetchone() is None:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS op_not_checker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT NOT NULL
            )
        ''')
        print('Таблица "op_not_checker" создана')
    else:
        print('Выполнено подключение к таблице "op_not_checker".')
    
    if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="checker_op"').fetchone() is None:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checker_op (
                user_id INTEGER,
                op_id INTEGER,
                PRIMARY KEY (user_id, op_id),
                FOREIGN KEY (op_id) REFERENCES op_not_checker(id)
            )
        """)
        print('Таблица "checker_op" создана')
    else:
        print('Выполнено подключение к таблице "checker_op".')
    
    conn.commit()
    conn.close()
    print('База данных успешно инициализирована.')


initialize_database()

def add_opnotcheck(link: str) -> bool:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO op_not_checker (link) VALUES (?)", (link,))
        conn.commit()
        return True

def get_link_by_id(id: int) -> str:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT link FROM op_not_checker WHERE id = ?", (id,))
        return cursor.fetchone()[0]

def delete_opnotcheck_by_link(link: str) -> bool:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM op_not_checker WHERE link = ?", (link,))
        conn.commit()
        return True

def get_all_id_opnotcheck():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM op_not_checker")
        return cursor.fetchall()
    
import sqlite3

def get_all_links_opnotcheck() -> list[str]:
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT link FROM op_not_checker")
            links = [row[0] for row in cursor.fetchall()]
            return links
    except sqlite3.Error as e:
        print(f"Ошибка доступа к базе данных: {e}")
        return []

    
def clear_opnotcheck() -> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM op_not_checker")
        conn.commit()

def mark_user_checked(user_id: int, op_id: int) -> bool:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO checker_op (user_id, op_id) VALUES (?, ?)", (user_id, op_id))
        conn.commit()
        return True

def has_user_checked(user_id: int, op_id: int) -> bool:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM checker_op WHERE user_id = ? AND op_id = ?", (user_id, op_id))
        return cursor.fetchone() is not None

def is_flyer_task_completed(task_hash):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT task_hash FROM flyer_task WHERE task_hash = ?", (task_hash,))
        return cursor.fetchone() is not None
    
def add_flyer_task(task_hash):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flyer_task (task_hash) VALUES (?)", (task_hash,))
        conn.commit()
        return True

def get_urls_by_id(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM task_data WHERE user_id = ?", (user_id,))
        return [row[0] for row in cursor.fetchall()]

def add_url(user_id, url):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO task_data (user_id, url) VALUES (?, ?)", (user_id, url))
        conn.commit()
        return True

def increment_counter_tasks(user_id, count):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET count_tasker = count_tasker + ? WHERE id = ?", (count, user_id))
        conn.commit()
        return True
    
def get_count_tasks(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count_tasker FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

def get_banned_user(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT banned FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
        
def set_banned_user(user_id, banned):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET banned = ? WHERE id = ?", (banned, user_id))
        conn.commit()
        return True
    
def delete_user(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True


def delete_utm(url):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utm_data WHERE url = ?", (url,))
        conn.commit()
        return True

def create_utm(url, count_users=0):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO utm_data (url, count_users) VALUES (?, ?)", (url, count_users))
        conn.commit()
        return True
    
def get_urls_utm():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM utm_data")
        return [row[0] for row in cursor.fetchall()]
    
def users_add_utm(url):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE utm_data SET count_users = count_users + 1 WHERE url = ?", (url,))
        conn.commit()
        return True
    
def users_add_utm_op(url):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE utm_data SET count_op_users = count_op_users + 1 WHERE url = ?", (url,))
        conn.commit()
        return True
    
def readd_username(id, username):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, id))
        conn.commit()
        return True

def get_username(id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT username FROM users WHERE id = ?", (id,)).fetchone()
        return result[0] if result else None

def users_utm_count(url):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count_users FROM utm_data WHERE url = ?", (url,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
        
def users_utm_count_op(url):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count_op_users FROM utm_data WHERE url = ?", (url,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

def get_id_from_username(username):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        return result[0] if result else None

def set_result(id_game, choice_first, choice_second):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        
        if choice_first == choice_second:
            result = "Ничья"
        elif choice_first == "stone" and choice_second == "scissors":
            # print(1)
            result = "Первый игрок победил!"
        elif choice_first == "scissors" and choice_second == "paper":
            result = "Первый игрок победил!"
        elif choice_first == "paper" and choice_second == "stone":
            result = "Первый игрок победил!"
        elif choice_first == "scissors" and choice_second == "stone":
            result = "Второй игрок победил!"
        elif choice_first == "paper" and choice_second == "scissors":
            result = "Второй игрок победил!"
        elif choice_first == "stone" and choice_second == "paper":
            result = "Второй игрок победил!"
        
        try:
            cursor.execute(
                "UPDATE knb SET result = ? WHERE id_game = ?",
                (result, id_game)
            )
            
            if result != "Ничья":
                bet = get_bet(id_game)
                winner = "first_player" if result.startswith("Первый") else "second_player"
                # print(winner)
                cursor.execute(
                    "SELECT first_player, second_player FROM knb WHERE id_game = ?",
                    (id_game,)
                )
                first_id, second_id = cursor.fetchone()
                winner_id = first_id if winner == "first_player" else second_id
            
            conn.commit()
            return result
        
        except Exception as e:
            conn.rollback()
            raise e

def get_bet(game_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute("SELECT bet FROM knb WHERE id_game = ?", (game_id,)).fetchone()[0]

def get_choice(player_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        if player_id == "first_player":
            return cursor.execute("SELECT choice_first FROM knb WHERE first_player = ?", (player_id,)).fetchone()[0]
        elif player_id == "second_player":
            return cursor.execute("SELECT choice_second FROM knb WHERE second_player = ?", (player_id,)).fetchone()[0]
        else:
            return None

def change_choice(game_id, player_id, choice):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        if player_id == "first_player":
            cursor.execute("UPDATE knb SET choice_first = ? WHERE id_game = ?", (choice, game_id))
        elif player_id == "second_player":
            cursor.execute("UPDATE knb SET choice_second = ? WHERE id_game = ?", (choice, game_id))
        conn.commit()
        return True

def get_knb_game(game_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute("SELECT * FROM knb WHERE id_game = ?", (game_id,)).fetchone()

def create_knb(first_player, second_player, choice_first=None, choice_second=None, result=None, bet=0):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO knb (first_player, second_player, choice_first, choice_second, result, bet) VALUES (?, ?, ?, ?, ?, ?)", (first_player, second_player, choice_first, choice_second, result, bet))
        game_id = cursor.lastrowid
        conn.commit()
        return game_id
    
def delete_knb(game_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knb WHERE id_game = ?", (game_id,))
        conn.commit()
        return True

def create_lottery(cash, ticket_cash):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lottery (status, cash, ticket_cash) VALUES ('enabled', ?, ?)", (cash, ticket_cash))
        conn.commit()
        return True
    
def finish_and_update_winner():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        active_lottery = cursor.execute("""
            SELECT id
            FROM lottery 
            WHERE status = 'enabled'
        """).fetchone()

        if not active_lottery:
            raise ValueError("Нет активной лотереи")

        lottery_id = active_lottery[0]


        participants = cursor.execute("""
            SELECT user_id, count_tickets 
            FROM lottery_data 
            WHERE count_tickets > 0 
            AND lottery_id = ?
        """, (lottery_id,)).fetchall()

        if not participants:
            raise ValueError("Нет участников с билетами")

        weighted_users = []
        for user_id, tickets in participants:
            weighted_users.extend([user_id] * tickets)

        winner_id = random.choice(weighted_users)

        cursor.execute("""
            UPDATE lottery 
            SET status = 'disabled', winner_id = ?
            WHERE id = ?
        """, (winner_id, lottery_id))

        conn.commit()
        return True, winner_id

def get_cash_in_lottery():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cash FROM lottery WHERE status = 'enabled'")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "Нет."
        
def get_ticket_cash_in_lottery():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_cash FROM lottery WHERE status = 'enabled'")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "Нет."
    
def get_id_lottery_enabled():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lottery WHERE status = 'enabled'")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "Нет."
        
def get_count_tickets_by_user(lottery_id, user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count_tickets FROM lottery_data WHERE lottery_id = ? AND user_id = ?", (lottery_id, user_id))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
        
def add_lottery_entry(lottery_id, user_id, username, cash, count_tickets=1):
    with sqlite3.connect(DATABASE_NAME) as conn:
        if username is None:
            username = "None"
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lottery_data 
            (lottery_id, user_id, username, count_tickets)
            VALUES (?, ?, ?, ?)
        """, (lottery_id, user_id, username, count_tickets))

        cursor.execute("""
            UPDATE lottery 
            SET cash = cash + ?
            WHERE id = ?
        """, (cash, lottery_id))
        conn.commit()
        return True
    
def get_active_lottery_id():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM lottery WHERE status = 'enabled'")
        result = cursor.fetchone()
        return result[0] if result else None

def add_or_update_user_boost(user_id, end_time):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM booster WHERE user_id = ?", (user_id,))
        existing_record = cursor.fetchone()
        
        if existing_record:
            cursor.execute("UPDATE booster SET end_time = ? WHERE user_id = ?", (end_time, user_id))
        else:
            cursor.execute("INSERT INTO booster (user_id, end_time) VALUES (?, ?)", (user_id, end_time))
        
        conn.commit()
        return True

def remove_user_boost(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM booster WHERE user_id = ?", (user_id,))
        conn.commit()
        return True

def check_and_remove_expired_boosts():
    current_time = datetime.now().timestamp()
    
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM booster WHERE end_time < ?", (current_time,))
            expired_users = cursor.fetchall()
            
            if expired_users:
                for (user_id,) in expired_users:
                    cursor.execute("DELETE FROM booster WHERE user_id = ?", (user_id,))
                    print(f"Удален буст для пользователя с ID: {user_id}")
                conn.commit()
            else:
                print("Нет просроченных бустов.")
    except Exception as e:
        print("Ошибка при удалении просроченных бустов:", e)

def user_in_booster(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM booster WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return True if result else False

def get_time_until_boost(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT end_time FROM booster WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            end_time = result[0]
            current_time = time.time()
            time_until_boost = end_time - current_time
            return time_until_boost
        else:
            return None

def get_clicks_by_period(period):
    if period not in ['day', 'week', 'month']:
        raise ValueError("Неизвестный период. Допустимые значения: 'day', 'week', 'month'")

    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            now_timestamp = time.time()
            now = datetime.fromtimestamp(now_timestamp, timezone.utc)

            if period == 'day':
                start_of_period = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
                time_threshold = start_of_period.timestamp()
                query = '''
                    SELECT SUM(click_count)
                    FROM click_times
                    WHERE last_click_time >= ?
                '''
                params = (time_threshold,)
            elif period == 'week':
                start_of_week = now - timedelta(days=now.weekday())
                start_of_period = datetime(start_of_week.year, start_of_week.month, start_of_week.day, tzinfo=timezone.utc)
                time_threshold = start_of_period.timestamp()
                query = '''
                    SELECT SUM(click_count)
                    FROM click_times
                    WHERE last_click_time >= ?
                '''
                params = (time_threshold,)
            elif period == 'month':
                query = '''
                    SELECT SUM(click_count)
                    FROM click_times
                '''
                params = ()

            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


def get_users_by_period(period):
    if period not in ['day', 'week', 'month']:
        raise ValueError("Недопустимый период. Ожидается 'day', 'week' или 'month'.")

    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            if cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users"').fetchone() is None:
                print('Таблица "users" не существует.')
                return 0

            if period == 'day':
                now = datetime.now(timezone.utc)
                start_of_period = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
                time_threshold = start_of_period.timestamp()
                query = '''
                    SELECT COUNT(*)
                    FROM users
                    WHERE registration_time >= ?
                '''
                params = (time_threshold,)
            elif period == 'week':
                now = datetime.now(timezone.utc)
                start_of_week = now - timedelta(days=now.weekday())
                start_of_period = datetime(start_of_week.year, start_of_week.month, start_of_week.day, tzinfo=timezone.utc)
                time_threshold = start_of_period.timestamp()
                query = '''
                    SELECT COUNT(*)
                    FROM users
                    WHERE registration_time >= ?
                '''
                params = (time_threshold,)
            elif period == 'month':
                query = '''
                    SELECT COUNT(*)
                    FROM users
                '''
                params = ()

            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return 0
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return 0

def change_status(id, status):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET status = ? WHERE id = ?', (status, id))
        conn.commit()
        return True

def get_username(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()[0]
    
def get_count_ref(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT count_refs FROM users WHERE id = ?', (user_id,)).fetchone()[0]

def get_user_referrals_count(referrer_id):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM users
                WHERE referral_id = ?;
            ''', (referrer_id,))
            result = cursor.fetchone()
            if result and result[0] is not None:
                return result[0]
            else:
                return 0
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None


def get_id_refferer(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT referral_id FROM users WHERE id = ?', (user_id,)).fetchone()[0]

def get_withdrawn(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT withdrawn FROM users WHERE id = ?', (user_id,)).fetchone()[0]
    
def get_top_balance():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT username, stars FROM users ORDER BY stars DESC LIMIT 50').fetchall()

def add_withdrawale(username, user_id, stars, status='Ожидает обработки ⚙️'):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO withdrawales (username, user_id, stars, status) VALUES (?, ?, ?, ?)', (username, user_id, stars, status))
        conn.commit()
        return True, cursor.lastrowid

def get_status_withdrawal(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT status FROM withdrawales WHERE user_id = ?', (user_id,)).fetchone()[0]

def get_withdrawals(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT * FROM withdrawales WHERE user_id = ?', (user_id,)).fetchall()

def get_count_clicks(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT click_count FROM click_times WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0
def add_promocode(code, stars, max_uses):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO promocodes (code, stars, max_uses) VALUES (?, ?, ?)',
                          (code, stars, max_uses))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
def get_all_promocodes():
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM promocodes")
            rows = cursor.fetchall()
            promocodes = [dict(row) for row in rows]
            return promocodes
    except sqlite3.Error as e:
        print(f"Ошибка доступа к базе данных: {e}")
        return []
def use_promocode(code, user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            promo = cursor.execute('''
                SELECT * FROM promocodes
                WHERE code = ? AND is_active = TRUE
                AND current_uses < max_uses
            ''', (code,)).fetchone()

            if not promo:
                return False, "Промокод недействителен или закончились использования"

            used = cursor.execute('''
                SELECT 1 FROM promocode_uses
                WHERE promocode_id = ? AND user_id = ?
            ''', (promo[0], user_id)).fetchone()

            if used:
                return False, "Вы уже использовали этот промокод"

            cursor.execute('''
                UPDATE promocodes
                SET current_uses = current_uses + 1
                WHERE code = ?
            ''', (code,))

            cursor.execute('''
                INSERT INTO promocode_uses (promocode_id, user_id)
                VALUES (?, ?)
            ''', (promo[0], user_id))

            cursor.execute('''
                UPDATE users
                SET stars = stars + ?
                WHERE id = ?
            ''', (promo[2], user_id))

            conn.commit()
            return True, promo[2]
        except Exception as e:
            conn.rollback()
            return False, f"❌ {str(e)}"

def get_user_refferals_list_and_username(user_id) -> list:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT id, username FROM users WHERE referral_id = ?', (user_id,)).fetchall()
    
def delete_promocode(code):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM promocodes WHERE code = ?', (code,))
        conn.commit()

def deactivate_promocode(code):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE promocodes SET is_active = FALSE WHERE code = ?', (code,))
        conn.commit()

def add_tasker(description, reward, link=None, boter=None, max_uses=0, channelprivate_id=0):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO new_tasks (description, reward, link, bot, max_completed, id_channel_private) VALUES (?, ?, ?, ?, ?, ?)',
                       (description, reward, link, boter, max_uses, channelprivate_id))
        conn.commit()

def increment_current_completed(task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE new_tasks SET current_completed = current_completed + 1 WHERE id = ?', (task_id,))
        conn.commit()

def get_current_completed(task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT current_completed FROM new_tasks WHERE id = ?', (task_id,)).fetchone()[0]
    
def get_max_completed(task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT max_completed FROM new_tasks WHERE id = ?', (task_id,)).fetchone()[0]

def deactivate_task(task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE new_tasks SET is_active = FALSE WHERE id = ?', (task_id,))
        conn.commit()

def delete_task(task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM new_tasks WHERE id = ?', (task_id,))
        conn.commit()

def get_active_tasks():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT * FROM new_tasks WHERE is_active = TRUE').fetchall()

def get_completed_tasks_for_user(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT task_id FROM completed_tasks WHERE user_id = ?', (user_id,))
        return [row[0] for row in cursor.fetchall()]

def complete_task_for_user(user_id, task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO completed_tasks (user_id, task_id) VALUES (?, ?)', (user_id, task_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False, "Вы уже выполняли это задание."
        except Exception as e:
            conn.rollback()
            return False

def get_task(task_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT * FROM new_tasks WHERE id = ?', (task_id,)).fetchone()

def get_user_count():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]

def get_total_withdrawn():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT COALESCE(SUM(withdrawn), 0.0) FROM users').fetchone()[0]

def get_normal_time_registration(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT registration_time FROM users WHERE id = ?', (user_id,)).fetchone()[0]

def update_click_count(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE click_times SET click_count = click_count + 1 WHERE user_id = ?', (user_id,))
        conn.commit()

def get_top_clicked():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT users.id, users.username, click_times.click_count
            FROM users
            JOIN click_times ON users.id = click_times.user_id
            ORDER BY click_times.click_count DESC
            LIMIT 10
        ''')
        return cursor.fetchall()

def get_last_daily_gift_time(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT last_claimed_time FROM daily_gifts WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def update_last_daily_gift_time(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO daily_gifts (user_id, last_claimed_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_claimed_time = ?
        ''', (user_id, time.time(), time.time()))
        conn.commit()

def get_last_click_time(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT last_click_time FROM click_times WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def update_last_click_time(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO click_times (user_id, last_click_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET last_click_time = ?
        ''', (user_id, time.time(), time.time()))
        conn.commit()

def get_users():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT id, username FROM users').fetchall()
    
def get_users_ids():
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users')
            return [str(row[0]) for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
def get_users_ids():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT id FROM users').fetchall()


def add_user(user_id, username, referral_id=None):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (id, username, stars, count_refs, referral_id) VALUES (?, ?, ?, ?, ?)',
                       (user_id, username, 0.0, 0, referral_id))
        conn.commit()

def add_withdrawal(user_id, amount):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET withdrawn = withdrawn + ? WHERE id = ?', (amount, user_id))
        conn.commit()

def get_balance_user(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT stars FROM users WHERE id = ?', (user_id,)).fetchone()
        return result[0]

def get_count_refs(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT count_refs FROM users WHERE id = ?', (user_id,)).fetchone()
        return result[0]

def user_exists(user_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        result = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return bool(result)

def increment_referrals(referrer_id):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET count_refs = count_refs + 1 WHERE id = ?', (referrer_id,))
        conn.commit()

def increment_stars(user_id, stars):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET stars = stars + ? WHERE id = ?', (stars, user_id))
        conn.commit()

def deincrement_stars(user_id, stars):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET stars = stars - ? WHERE id = ?', (stars, user_id))
        conn.commit()

def get_top_referrals():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT id, count_refs, username FROM users ORDER BY count_refs DESC LIMIT 10').fetchall()

def sum_all_stars():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT COALESCE(SUM(stars), 0.0) FROM users').fetchone()[0]

def sum_all_withdrawn():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        return cursor.execute('SELECT COALESCE(SUM(withdrawn), 0.0) FROM users').fetchone()[0]

def get_period_timestamps(period: str) -> tuple[int, int]:
    local_tz = ZoneInfo("Europe/Moscow")
    now_local = datetime.now(local_tz)

    if period == 'day':
        start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1) - timedelta(seconds=1)
    elif period == 'week':
        start = now_local - timedelta(days=now_local.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7) - timedelta(seconds=1)
    elif period == 'month':
        start = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1)
        else:
            next_month = start.replace(month=start.month + 1)
        end = next_month - timedelta(seconds=1)
    else:
        raise ValueError("Неверный период времени")
    
    return int(start.timestamp()), int(end.timestamp())

def get_top_referrals_formatted(period: str) -> list[str]:
    try:
        start_ts, end_ts = get_period_timestamps(period)
    except ValueError as ve:
        return [str(ve)]
    
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u2.id, u2.username, COUNT(u1.id) as referral_count
                FROM users u1
                JOIN users u2 ON u1.referral_id = u2.id
                WHERE u1.referral_id IS NOT NULL
                AND u1.registration_time BETWEEN ? AND ?
                GROUP BY u2.id
                HAVING referral_count > 0
                ORDER BY referral_count DESC
                LIMIT 5;
            ''', (start_ts, end_ts))
            top_referrals = cursor.fetchall()
    except Exception as e:
        return [f"Ошибка при получении топа рефералов: {e}"]
    
    if not top_referrals:
        return ["Нет данных о рефералах за выбранный период."]
    
    places = ["🥇", "🥈", "🥉"]
    formatted_referrals = []
    for i, (user_id, username, count) in enumerate(top_referrals):
        place = places[i] if i < 3 else '✨'
        name = username if username else f"Пользователь {user_id}"
        formatted_referrals.append(f"{place} <b>{name}</b> | Рефералов: <code>{count}</code>")
    
    return formatted_referrals

def get_weekly_referrals(user_id: int) -> int:
    try:
        start_ts, end_ts = get_period_timestamps('week')
    except ValueError as ve:
        return 0
    
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM users
                WHERE referral_id = ?
                AND registration_time BETWEEN ? AND ?
            ''', (user_id, start_ts, end_ts))
            result = cursor.fetchone()
    except Exception as e:
        return 0
    
    return result[0] if result else 0

def get_user_referral_rank_formatted(user_id: int, period: str) -> str:
    try:
        start_ts, end_ts = get_period_timestamps(period)
    except ValueError as ve:
        return str(ve)
    
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(id)
                FROM users
                WHERE referral_id = ? AND registration_time BETWEEN ? AND ?
            ''', (user_id, start_ts, end_ts))
            user_referral_count = cursor.fetchone()[0]

            cursor.execute('''
                SELECT COUNT(DISTINCT referral_count) + 1
                FROM (
                    SELECT referral_id, COUNT(id) AS referral_count
                    FROM users
                    WHERE registration_time BETWEEN ? AND ?
                    GROUP BY referral_id
                    HAVING referral_count > 0
                ) AS referral_counts
                WHERE referral_count > ?
            ''', (start_ts, end_ts, user_referral_count))
            result = cursor.fetchone()
            rank_value = result[0] if result else 1
    except Exception as e:
        return f"Ошибка при получении вашего места в топе: {e}"
    
    if user_referral_count > 0:
        return f"<b>🏅 Ты на {rank_value} месте</b> | <code>{user_referral_count}</code> рефералов."
    else:
        return f"<b>🚫 Ты не попал в топ!</b> | <code>{user_referral_count}</code> рефералов."
