import sqlite3
import random
import string

DB_PATH = "kiosk.db"

def gen_code(length=6):
    """6 xonali raqamli login kod yaratadi."""
    return "".join(random.choices(string.digits, k=length))


conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    last_name    TEXT    NOT NULL,      -- ← add this
    age          INTEGER NOT NULL,
    gender       TEXT    NOT NULL,
    phone        TEXT    NOT NULL UNIQUE,
    photo_path   TEXT
)
''')

# 3) receptions jadvali — receptionlar va ularning Telegram login kodlari
c.execute('''
CREATE TABLE IF NOT EXISTS receptions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    chat_id     INTEGER,           -- bot orqali login qilgach to‘ldiriladi
    login_code  TEXT    UNIQUE     -- reception botga kirish kodi
)
''')

# 4) visits jadvali — har bir xizmat chaqirig‘i alohida yozuv
c.execute('''
CREATE TABLE IF NOT EXISTS visits (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id         INTEGER NOT NULL,
    check_in          TEXT    NOT NULL,      -- xizmat boshlangan vaqti
    check_out         TEXT,                   -- tugagan vaqti
    service           TEXT    NOT NULL,      -- tanlangan xizmat
    status            TEXT,
    reception_id      INTEGER,               -- kim xizmat qildi
    reception_comment TEXT,                  -- reception izohi
    visit_token       TEXT    UNIQUE,        -- bir martalik ID
    FOREIGN KEY(client_id)    REFERENCES clients(id),
    FOREIGN KEY(reception_id) REFERENCES receptions(id)
)
''')


initial_receptions = [
    ("Asliddin Tursunov", None, 12345678),
 
]
c.executemany('''
  INSERT OR IGNORE INTO receptions (name, chat_id, login_code)
  VALUES (?, ?, ?)
''', initial_receptions)


conn.commit()
conn.close()

print("DB tayyorlandi!")
