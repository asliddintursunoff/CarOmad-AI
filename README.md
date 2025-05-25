
# Avtosalon Analitika Platformasi

Zamonaviy avtomobil salonlari uchun — mijozlarni avtomatik ro‘yxatdan o‘tkazish, yuzni tanish, statistika va AI yordamida potensial xaridorlarni bashorat qilish uchun to‘liq yechim.

---

## 🔥 Tuzilishi

```
/backend.py       # FastAPI backend (API, ML, tahlil, frontendga data)
/main.py          # Barcha subsystemlarni birga ishga tushiruvchi nuqta
/bot.py           # Telegram bot reception va xodimlar uchun
/kiosk.py         # Tkinter GUI – ro‘yxat va kamera orqali yuzni tanish terminali
/face_utils.py    # Yuzni tanish (OpenCV, LBPH, etc.)
/exit_detector.py # Avtosalonni tark etishni aniqlash (kamera orqali)
/db_init.py       # Bazani yaratish va dastlabki ma’lumotlar kiritish
/ml_model.pkl     # ML modeli fayli (LogisticRegression, pickle orqali)
/kiosk.db         # SQLite ma’lumotlar bazasi
/requirements.txt # Kerakli Python kutubxonalar ro‘yxati
/static/
    stats.html      # Statistik tahlil va grafik interfeys
    clients.html    # Mijozlar ro‘yxati
    potential.html  # Potensial xaridorlar (AI asosida)
    style.css       # Dizayn
/contracts/         # PDF shartnomalar, passportlar
/photos/            # Mijoz fotosuratlari
```

---

## 1️⃣ Muhit va Kutubxonalar

```bash
python3 -m venv kiosk_env
source kiosk_env/bin/activate
pip install -r requirements.txt
```
**`requirements.txt`** faylida barcha kerakli kutubxonalar (fastapi, uvicorn, scikit-learn, pandas, opencv-python, python-telegram-bot, pillow, ...) mavjud.

---

## 2️⃣ Ma’lumotlar Bazasi va Dastlabki Ma’lumot

**Bazani yaratish va to‘ldirish uchun:**
```bash
python db_init.py
```
Bu komanda `kiosk.db` faylini yaratadi va namunaviy mijozlar, tashriflar, receptionlarni bazaga joylaydi.

---

## 3️⃣ ML Modelini Tayyorlash

Yangi mijozlar yoki tashriflar qo‘shilganda, AI modelini yangilang:
```bash
python demo.py
```
Yoki agar `train_model.py` bo‘lsa, shuni ishga tushiring.

> Natijada **ml_model.pkl** fayli yangilanadi.

---

## 4️⃣ Backend va Frontend

**Backend (API) ni ishga tushurish:**
```bash
uvicorn backend:app --reload
```
- **API endpointlar:** `/api/clients`, `/api/stats`, `/api/potential_buyers_ml`, `/api/retrain_model`
- **Statik fayllar:** `/static/` papkada, frontend uchun HTML/CSS/JS

**Frontend ishlatish:**
- Brauzerda `static/stats.html` (statistika, grafiklar), `static/clients.html` (mijozlar), `static/potential.html` (AI xaridor bashorati) oching.

---

## 5️⃣ Telegram Bot va Kiosk

**Telegram botni ishga tushirish:**
```bash
python bot.py
```
Reception va xodimlar uchun, mijozlar harakati va xizmatlarni kuzatish, xabar yuborish uchun.

**Kiosk/terminal (kompyuter yoki sensorli ekran):**
```bash
python kiosk.py
```
Mijozlarni kamera orqali yuzni tanib, avtomatik ro‘yxatdan o‘tkazadi.

---

## 6️⃣ Barchasini Birga Ishga Tushirish

Hammasini bitta komandada (parallel):
```bash
python main.py
```
- FastAPI backend, bot.py va kiosk.py multiprocessing orqali ishga tushadi.

---

## 📊 Asosiy Imkoniyat va Sahifalar

- **Mijozlar, tashriflar va receptionlar**: to‘liq boshqaruv va monitoring
- **Statistika va grafiklar**: xizmatlar, tashriflar, yosh/jins/soat kesimida tahlil
- **AI (ML) yordamida potensial xaridorlarni aniqlash**: Logistic Regression asosida bashorat
- **Frontend sahifalar**:
    - `static/stats.html` — statistika va grafik
    - `static/clients.html` — mijozlar ro‘yxati
    - `static/potential.html` — AI xaridor bashorati
- **Telegram bot**: reception monitoring va notifikatsiya
- **Kiosk**: yuzni tanish va tez ro‘yxatdan o‘tkazish

---

## ⚙️ Ishlash mantiqi

- **Ma’lumotlar bazasi** — barcha ma’lumotlar (`kiosk.db`) SQLite bazasida
- **AI/ML modeli** — Logistic Regression (`ml_model.pkl`), har bir mijoz uchun sotib olish ehtimolini hisoblaydi
- **API** — FastAPI orqali barcha kerakli malumotlarni frontend va boshqa modullarga beradi
- **Bot va kiosk** — reception va mijozlar bilan ishlashni soddalashtiradi
- **Frontend** — HTML/CSS/JS, responsive va o‘zaro bog‘langan

---

## 🧩 Muammolar va Maslahatlar

- **ML model ishlamasa:** Yangi ma’lumotlardan so‘ng modelni qayta train qiling (`python demo.py`)
- **Frontendda natija chiqmasa:** API ishlayotganiga va baza to‘g‘ri to‘ldirilganiga ishonch hosil qiling
- **Bot/kiosk xatoliklari:** Kutubxonalar va mos ruxsatlar borligiga ishonch hosil qiling (token, kamera)
- **Visit_token:** har bir tashrif uchun `uuid.uuid4()` orqali unikal token hosil qiling

---

## 🧑‍💻 Qisqacha Loyihaning Ishlash Printsipi

1. **Mijozlar** va **vizitlar** bazaga kiritiladi
2. **AI model** har bir mijoz uchun xarid ehtimolini hisoblaydi (yosh, jins, tashriflar soni, test-drive soni va boshqalar)
3. **Tahlil va monitoring** HTML/CSS/JS orqali qulay va chiroyli interfeysda ko‘rsatiladi
4. **Telegram bot** va **kiosk** yordamida real vaqtda boshqaruv va monitoring
5. **Kengaytirish va integratsiya qilish juda oson!**

---

## 📝 Loyihani muallifi

> [Tursunov Asliddin]

---

**Savollar va yangi imkoniyatlar uchun:**
> [email, telegram, yoki boshqa kontakt]
