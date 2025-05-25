import sqlite3
import uuid
DB = 'kiosk.db'

clients = [
    ('Sardor', 'Tursunov', 32, 'male', '998911234567', None),
    ('Dilshod', 'Karimov', 28, 'male', '998901234567', None),
    ('Sevara', 'Qodirova', 26, 'female', '998935432100', None),
    ('Madina', 'Toirova', 38, 'female', '998997654321', None),
    ('Azamat', 'Jalilov', 45, 'male', '998932222222', None),
    ('Javohir', 'Yuldashev', 29, 'male', '998933456789', None),
    ('Gulnoza', 'Ismoilova', 33, 'female', '998936789012', None),
    ('Ulug‘bek', 'Aliyev', 41, 'male', '998907654321', None),
    ('Ozoda', 'Sharipova', 25, 'female', '998939999111', None),
    ('Shaxzod', 'Bekmurodov', 37, 'male', '998939876543', None),
    ('Maftuna', 'Raximova', 31, 'female', '998931234567', None),
    ('Doston', 'G‘aniyev', 27, 'male', '998938765432', None),
    ('Umida', 'Xolmatova', 24, 'female', '998935554433', None),
    ('Kamola', 'Davronova', 36, 'female', '998934444555', None),
    ('Ibrohim', 'Matmurodov', 43, 'male', '998931112233', None),
    ('Shohruh', 'Eshmatov', 39, 'male', '998932223344', None),
    ('Dilafruz', 'Ergasheva', 28, 'female', '998930001122', None),
    ('Rustam', 'Yusupov', 35, 'male', '998934567890', None),
    ('Sitora', 'Sodiqova', 30, 'female', '998930012345', None),
    ('Jasur', 'Nurmatov', 44, 'male', '998938888222', None),
]


receptions = [
   
]

visits = [
    (1, '2024-05-01 10:00:00', '2024-05-01 10:40:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (1, '2024-05-03 15:30:00', '2024-05-03 16:00:00', 'purchase', 'purchased', 1, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (2, '2024-05-02 12:00:00', '2024-05-02 12:45:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (2, '2024-05-06 11:20:00', '2024-05-06 11:45:00', 'consultation', None, 2, None, str(uuid.uuid4())),
    (3, '2024-05-04 09:00:00', '2024-05-04 09:25:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (3, '2024-05-05 10:10:00', '2024-05-05 10:35:00', 'consultation', None, 1, None, str(uuid.uuid4())),
    (4, '2024-05-06 13:00:00', '2024-05-06 13:30:00', 'purchase', 'purchased', 2, 'Sotib oldi', str(uuid.uuid4())),
    (5, '2024-05-07 16:00:00', '2024-05-07 16:30:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (6, '2024-05-03 11:00:00', '2024-05-03 11:30:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (6, '2024-05-05 14:15:00', '2024-05-05 14:45:00', 'consultation', None, 3, None, str(uuid.uuid4())),
    (7, '2024-05-08 12:40:00', '2024-05-08 13:05:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (7, '2024-05-11 10:20:00', '2024-05-11 10:50:00', 'purchase', 'purchased', 3, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (8, '2024-05-09 15:10:00', '2024-05-09 15:35:00', 'consultation', None, 1, None, str(uuid.uuid4())),
    (9, '2024-05-10 14:20:00', '2024-05-10 14:50:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (9, '2024-05-14 09:45:00', '2024-05-14 10:15:00', 'purchase', 'purchased', 2, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (10, '2024-05-12 12:00:00', '2024-05-12 12:30:00', 'consultation', None, 3, None, str(uuid.uuid4())),
    (11, '2024-05-06 09:00:00', '2024-05-06 09:25:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (11, '2024-05-09 11:20:00', '2024-05-09 11:45:00', 'consultation', None, 2, None, str(uuid.uuid4())),
    (11, '2024-05-10 16:00:00', '2024-05-10 16:30:00', 'purchase', 'purchased', 2, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (12, '2024-05-08 13:40:00', '2024-05-08 14:10:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (12, '2024-05-13 17:00:00', '2024-05-13 17:30:00', 'consultation', None, 1, None, str(uuid.uuid4())),
    (13, '2024-05-11 08:10:00', '2024-05-11 08:40:00', 'test-drive', None, 3, None, str(uuid.uuid4())),
    (13, '2024-05-13 15:30:00', '2024-05-13 15:55:00', 'purchase', 'purchased', 3, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (14, '2024-05-10 12:20:00', '2024-05-10 12:50:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (15, '2024-05-09 14:00:00', '2024-05-09 14:30:00', 'consultation', None, 2, None, str(uuid.uuid4())),
    (15, '2024-05-12 15:30:00', '2024-05-12 16:00:00', 'purchase', 'purchased', 1, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (16, '2024-05-13 16:40:00', '2024-05-13 17:10:00', 'test-drive', None, 3, None, str(uuid.uuid4())),
    (17, '2024-05-07 10:30:00', '2024-05-07 11:00:00', 'consultation', None, 2, None, str(uuid.uuid4())),
    (17, '2024-05-14 12:15:00', '2024-05-14 12:45:00', 'purchase', 'purchased', 1, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (18, '2024-05-08 10:00:00', '2024-05-08 10:30:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (18, '2024-05-12 13:00:00', '2024-05-12 13:25:00', 'consultation', None, 3, None, str(uuid.uuid4())),
    (19, '2024-05-14 09:00:00', '2024-05-14 09:30:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (19, '2024-05-17 15:20:00', '2024-05-17 15:50:00', 'purchase', 'purchased', 2, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (20, '2024-05-15 11:00:00', '2024-05-15 11:30:00', 'test-drive', None, 3, None, str(uuid.uuid4())),
    (20, '2024-05-19 14:00:00', '2024-05-19 14:25:00', 'consultation', None, 2, None, str(uuid.uuid4())),

    # Qo‘shimcha tashriflar
    (6, '2024-05-15 13:10:00', '2024-05-15 13:30:00', 'purchase', 'purchased', 3, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (9, '2024-05-16 10:20:00', '2024-05-16 10:50:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (12, '2024-05-18 14:10:00', '2024-05-18 14:40:00', 'purchase', 'purchased', 2, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (14, '2024-05-17 11:30:00', '2024-05-17 12:00:00', 'consultation', None, 1, None, str(uuid.uuid4())),
    (7, '2024-05-18 15:40:00', '2024-05-18 16:10:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (17, '2024-05-19 11:50:00', '2024-05-19 12:20:00', 'test-drive', None, 3, None, str(uuid.uuid4())),
    (20, '2024-05-21 09:10:00', '2024-05-21 09:40:00', 'purchase', 'purchased', 1, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (10, '2024-05-20 10:00:00', '2024-05-20 10:30:00', 'purchase', 'purchased', 2, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (18, '2024-05-21 12:00:00', '2024-05-21 12:30:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (2, '2024-05-22 13:00:00', '2024-05-22 13:30:00', 'consultation', None, 3, None, str(uuid.uuid4())),
    (15, '2024-05-22 14:30:00', '2024-05-22 15:00:00', 'test-drive', None, 1, None, str(uuid.uuid4())),
    (1, '2024-05-23 15:10:00', '2024-05-23 15:40:00', 'test-drive', None, 3, None, str(uuid.uuid4())),
    (11, '2024-05-24 09:00:00', '2024-05-24 09:30:00', 'purchase', 'purchased', 1, 'Mijoz mashina oldi', str(uuid.uuid4())),
    (7, '2024-05-25 13:10:00', '2024-05-25 13:40:00', 'test-drive', None, 2, None, str(uuid.uuid4())),
    (13, '2024-05-26 11:20:00', '2024-05-26 11:50:00', 'test-drive', None, 3, None, str(uuid.uuid4())),
]


conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Clients
c.executemany('''
    INSERT OR IGNORE INTO clients (name, last_name, age, gender, phone, photo_path)
    VALUES (?, ?, ?, ?, ?, ?)
''', clients)

# 2. Receptions
c.executemany('''
    INSERT OR IGNORE INTO receptions (name, chat_id, login_code)
    VALUES (?, ?, ?)
''', receptions)

# 3. Visits
c.executemany('''
    INSERT INTO visits (client_id, check_in, check_out, service, status, reception_id, reception_comment, visit_token)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', visits)

conn.commit()
conn.close()

print("Demo ma'lumotlar muvaffaqiyatli qo'shildi!")
