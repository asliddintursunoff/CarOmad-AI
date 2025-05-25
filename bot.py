import sqlite3
import os
import asyncio
import traceback
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from passporteye import read_mrz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

TOKEN = '7795971660:AAGOdPkvvk-VAlpUQOWIACEVQsOGZsFGLIo'
app = ApplicationBuilder().token(TOKEN).build()
BOT_LOOP = None

# Avtomobil tanlovlari
CARS = {
    "COBALT": {
        "rangi": [("GAZ", "Oq (Summit White)"), ("GWT", "Kul (Abalone White)")],
        "narx": "146 757 000"
    },
    "ONIX": {
        "rangi": [("GAR", "Qora (Black Noir)"), ("GAZ", "Oq (Summit White)")],
        "narx": "171 000 000"
    },
    "GENTRA": {
        "rangi": [("GAZ", "Oq"), ("GAR", "Qora")],
        "narx": "150 000 000"
    }
}
CAR_LIST = list(CARS.keys())

(
    SELECT_STATUS,
    WAIT_PASSPORT,
    WAIT_CAR_MODEL,
    WAIT_CAR_COLOR,
    CONFIRM_CONTRACT,
    WAIT_COMMENT,
    AFTER_STATUS
) = range(7)

def assign_reception_and_notify(client_id: int, client_name: str, purpose: str, visit_id: int):
    try:
        conn = sqlite3.connect('kiosk.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, name, chat_id
            FROM receptions
            ORDER BY (
                SELECT COUNT(*) FROM visits WHERE visits.reception_id = receptions.id AND visits.check_out IS NULL
            ) ASC
            LIMIT 1
        ''')
        row = c.fetchone()
        if not row:
            print("[ERROR] No receptions found")
            return
        rec_id, rec_name, chat_id = row
        c.execute('UPDATE visits SET reception_id=? WHERE id=?', (rec_id, visit_id))
        conn.commit()
        conn.close()
        text = (
            f"🆕 Yangi mijoz (ID: {visit_id})\n"
            f"Mijoz ID: {client_id}\n"
            f"Ism: {client_name}\n"
            f"Maqsad: {purpose}\n"
            f"Navbat raqami: {visit_id}\n"
            f"Reception: {rec_name}"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Status", callback_data=f"action_status|{visit_id}")],
            [InlineKeyboardButton("Tugatish", callback_data=f"finish|{visit_id}")]
        ])
        asyncio.run_coroutine_threadsafe(
            app.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard),
            BOT_LOOP
        )
    except Exception as e:
        print(f"[ERROR] assign_reception_and_notify: {e}\n{traceback.format_exc()}")

async def initial_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    action, vid = update.callback_query.data.split('|')
    vid = int(vid)
    context.user_data['visit_id'] = vid
    await update.callback_query.answer()
    if action == 'finish':
        try:
            conn = sqlite3.connect('kiosk.db')
            c = conn.cursor()
            c.execute("UPDATE visits SET check_out=? WHERE id=?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vid))
            conn.commit()
            conn.close()
            await update.callback_query.edit_message_text("✅ Chat tugatildi.")
            return ConversationHandler.END
        except Exception as e:
            await update.callback_query.edit_message_text("Xatolik. Qayta urinib ko'ring.")
            return ConversationHandler.END
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Sotib oldi", callback_data=f"status_bought|{vid}")],
        [InlineKeyboardButton("O'ylab ko'rdi", callback_data=f"status_consider|{vid}")],
        [InlineKeyboardButton("Test drive qildi", callback_data=f"status_testdrive|{vid}")],
        [InlineKeyboardButton("Shartnoma tuzish", callback_data=f"status_contract|{vid}")]
    ])
    await update.callback_query.edit_message_text("Iltimos, statusni tanlang:", reply_markup=kb)
    return SELECT_STATUS

async def status_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    data, vid = update.callback_query.data.split('|')
    vid = int(vid)
    context.user_data['visit_id'] = vid
    status_key = data.replace('status_', '')
    try:
        conn = sqlite3.connect('kiosk.db')
        c = conn.cursor()
        c.execute('UPDATE visits SET status=? WHERE id=?', (status_key, vid))
        conn.commit()
        conn.close()
    except Exception:
        await update.callback_query.edit_message_text("Xatolik. Qayta urinib ko'ring.")
        return ConversationHandler.END
    if status_key == 'contract':
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        await update.callback_query.message.reply_text("Iltimos, mijoz pasportini (jpg/png) yuboring.")
        return WAIT_PASSPORT
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Tugatish", callback_data=f"finish|{vid}")],
        [InlineKeyboardButton("Comment", callback_data=f"comment|{vid}")]
    ])
    await update.callback_query.edit_message_reply_markup(reply_markup=kb)
    return AFTER_STATUS

async def passport_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        file_obj = None
        if update.message.photo:
            file_obj = await update.message.photo[-1].get_file()
        elif update.message.document and update.message.document.mime_type.startswith('image/'):
            file_obj = await update.message.document.get_file()
        if not file_obj:
            await update.message.reply_text("Iltimos, pasport rasmni yuboring (jpg/png/foto).")
            return WAIT_PASSPORT
        os.makedirs('contracts', exist_ok=True)
        path = os.path.join('contracts', f"passport_{update.message.message_id}.jpg")
        await file_obj.download_to_drive(path)
        mrz = read_mrz(path)
        if mrz is None:
            await update.message.reply_text("MRZ topilmadi, aniqroq rasm yuboring.")
            return WAIT_PASSPORT
        context.user_data.update({
            'surname': mrz.surname or "",
            'names': mrz.names or "",
            'passport_no': mrz.number or "",
            'dob': mrz.date_of_birth or "",
        })
        
        try:
            vid = context.user_data['visit_id']
            conn = sqlite3.connect('kiosk.db')
            c = conn.cursor()
            c.execute('SELECT c.phone FROM clients c JOIN visits v ON v.client_id = c.id WHERE v.id=?', (vid,))
            row = c.fetchone()
            if row:
                context.user_data['phone'] = row[0]
        except Exception:
            context.user_data['phone'] = ""
   
        kb = [[InlineKeyboardButton(model, callback_data=f"car_{model}")] for model in CAR_LIST]
        await update.message.reply_text("Avtomobil modelini tanlang:", reply_markup=InlineKeyboardMarkup(kb))
        return WAIT_CAR_MODEL
    except Exception as e:
        await update.message.reply_text("Xatolik yuz berdi. Qayta urinib ko'ring.")
        return WAIT_PASSPORT

async def car_model_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    model = query.data.replace("car_", "")
    context.user_data['car_model'] = model
    # Rang tugmalarini tayyorlash
    kb = [[InlineKeyboardButton(name, callback_data=f"color_{code}")] for code, name in CARS[model]["rangi"]]
    await query.edit_message_text("Avtomobil rangini tanlang:", reply_markup=InlineKeyboardMarkup(kb))
    return WAIT_CAR_COLOR

async def car_color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    color_code = query.data.replace("color_", "")
    model = context.user_data['car_model']
    color_name = [name for code, name in CARS[model]["rangi"] if code == color_code][0]
    context.user_data['car_color'] = color_name
    context.user_data['car_price'] = CARS[model]['narx']
    await query.edit_message_text(
        f"Model: {model}\nRang: {color_name}\nNarx: {CARS[model]['narx']}\n"
        f"Avtomobilni tasdiqlaysizmi?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Tasdiqlash", callback_data="confirm_contract")]])
    )
    return CONFIRM_CONTRACT

async def confirm_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Shartnoma tayyorlanmoqda...")
    await create_contract_pdf(update, context)
    vid = context.user_data['visit_id']
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Tugatish", callback_data=f"finish|{vid}")],
        [InlineKeyboardButton("Comment", callback_data=f"comment|{vid}")]
    ])
    await update.callback_query.message.reply_text("Iltimos, yakuniy holatni tanlang:", reply_markup=kb)
    return AFTER_STATUS

async def create_contract_pdf(update, context):
  
    vid = context.user_data.get('visit_id', '-')
    surname = context.user_data.get('surname', '')
    names = context.user_data.get('names', '')
    passport_no = context.user_data.get('passport_no', '')
    dob = context.user_data.get('dob', '')
    phone = context.user_data.get('phone', '')
    car_model = context.user_data.get('car_model', '')
    car_color = context.user_data.get('car_color', '')
    car_price = context.user_data.get('car_price', '')
    sana = datetime.now().strftime('%d.%m.%Y')

    # Fayl yo‘li
    os.makedirs('contracts', exist_ok=True)
    pdf_path = os.path.join('contracts', f"shartnoma_{vid}.pdf")

    # PDF yaratish
    cpdf = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4
    y = h - 40

    # Sarlavha
    cpdf.setFont("Helvetica-Bold", 13)
    cpdf.drawString(70, y, f"AVTOMOBIL SOTIB OLISH BO'YICHA SHARTNOMA №{vid}")
    y -= 30

    # Asosiy ma'lumotlar
    cpdf.setFont("Helvetica", 11)
    cpdf.drawString(60, y, f"Sana: {sana}")
    y -= 20
    cpdf.drawString(60, y, f"Ism, familiya: {surname} {names}")
    y -= 20
    cpdf.drawString(60, y, f"Telefon: {phone}")
    y -= 20
    cpdf.drawString(60, y, f"Passport: {passport_no}")
    y -= 20
    cpdf.drawString(60, y, f"Tug'ilgan sana: {dob}")
    y -= 20
    cpdf.setFont("Helvetica-Bold", 11)
    cpdf.drawString(60, y, f"Avtomobil: {car_model} | Rang: {car_color} | Narx: {car_price} so'm")
    y -= 30


    cpdf.setFont("Helvetica", 10)
    lines = ["«Lux Auto Motors» MCHJ, nomidan harakat qiluvchi Agzamov Sardor Saidinovich, Ustav asosida, "
        "AO «UzAuto Motors» bilan Dilerlik Shartnomasi №DSD-2019-71 01.07.2019 yildan, "
        "qonuniy tijorat vakil sifatida, kelgusida «Diler» deb ataluvchi bir tomondan, va ",
        f"fuqarosi {surname} {names} (pasport: {passport_no}, berilgan sana: {dob}), "
        "kelgusida «Xaridor» deb ataluvchi ikkinchi tomondan, "
        "birgalikda «Tomonlar», alohida-alohida «Tomon» deb yuritiladi, "
        "O‘zbekiston Respublikasi «Iste’molchilar huquqlarini himoya qilish to‘g‘risida»gi Qonuniga muvofiq "
        "quyidagilar to‘g‘risida kelishib, ushbu Shartnomani tuzdilar:",
        "",

        "1. SHARTNOMA PREDMETI",
        "1.1. Ushbu Shartnoma bo‘yicha Diler AO «UzAuto Motors»da Xaridor buyurtmasini qabul qiladi va avtomobilni "
        "buyurtma asosida yetkazib beradi. Xaridor esa to‘lovni amalga oshirib, avtomobilni oladi.",
        "1.2. Ishlab chiqaruvchi elektron komponentlar yetishmovchiligi yoki logistik muammolar sababli "
        "yetkazib berish muddatini uzaytirishi mumkin. Xaridor buni tan oladi va Shartnoma bandlaridan kelib chiqib "
        "talablarni bajara olmaslik bo‘yicha da’vo qilmaydi.",
        "1.3. Tovar sertifikatlangan. Sertifikat va avtomobil opsiyalari ishlab chiqaruvchi saytida mavjud: "
        "http://www.uzautomotors.com",
        "",

        "2. TOVAR NARXI VA TO‘LOV TARTIBI",
        f"2.1. Model, modifikatsiya, narx, son va umumiy summa: {car_model} ({car_color}) - {car_price} so‘m.",
        "2.2. To‘lovlar milliy valyutada amalga oshiriladi (so‘mda) AO «UzAuto Motors» hisobiga.",
        "2.3. Xaridor 7 kun ichida qiymatning 50%ini to‘laydi, qolganini to‘liq to‘lovgacha to‘laydi. "
        "Agar muddat buzilsa, Shartnoma bekor qilinadi.",
        "2.4. Qo‘shimcha opsiyalar bo‘lsa, xaridor tovarni qabul qilmaslik, narx farqini to‘lash yoki boshqa model tanlash huquqiga ega.",
        "",

        "3. YETKAZIB BERISH MUDDATI VA SHARTLARI",
        "3.1. Avtomobil 30-noyabr 2024-yilgacha yetkaziladi. Maxsus holatlarda muddat 45 kungacha cho‘zilishi mumkin.",
        "3.2. To‘liq to‘lovdan so‘ng xaridorga avto salondan avtomobil beriladi.",
        "3.3. Xaridor avtomobil sifatini qabul qilishda tekshiradi, nuqson bo‘lsa dalolatnoma tuziladi.",
        "",

        "4. TOMONLARNING HUQUQLARI VA MAJBURIYATLARI",
        "4.1. Diler avtomobilni kafolatli, to‘liq, hujjatlar bilan yetkazib beradi.",
        "4.2. Xaridor to‘liq to‘lov qiladi, avtomobilni olib ketadi va foydalanish qoidalariga amal qiladi.",
        "",

        "5. FORS-MAJOR",
        "5.1. Tabiiy ofatlar, urush, davlat qarorlari, fors-major holatlari bo‘lsa, majburiyatlar to‘xtatiladi.",
        "",

        "6. BOSHQA SHARTLAR",
        "6.1. Shartnoma ikki nusxada tuziladi, kuchga kiradi va tomonlar imzolagandan so‘ng amal qiladi.",
        "",

        "Diler: ______________________",
        "Xaridor: ____________________"
    ]
    for line in lines:
        cpdf.drawString(60, y, line)
        y -= 18

    cpdf.save()

    # Yuborish
    await update.effective_message.reply_document(open(pdf_path, 'rb'))

# Standart after-status, comment, finish
async def finish_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    _, vid = update.callback_query.data.split('|')
    vid = int(vid)
    try:
        conn = sqlite3.connect('kiosk.db')
        c = conn.cursor()
        c.execute("UPDATE visits SET check_out=? WHERE id=?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vid))
        conn.commit()
        conn.close()
        await update.callback_query.edit_message_text("✅ Mijoz bilan ish yakunlandi.")
        return ConversationHandler.END
    except Exception as e:
        await update.callback_query.edit_message_text("Xatolik yuz berdi. Qayta urinib ko'ring.")
        return ConversationHandler.END

async def comment_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, vid = query.data.split('|')
    vid = int(vid)
    context.user_data['visit_id'] = vid
    await query.edit_message_text("Iltimos, reception izohini yuboring.")
    return WAIT_COMMENT

async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        text = update.message.text
        vid = context.user_data.get('visit_id')
        if vid is None:
            await update.message.reply_text("Xatolik: visit_id topilmadi. Qayta urinib ko'ring.")
            return ConversationHandler.END
        conn = sqlite3.connect('kiosk.db')
        c = conn.cursor()
        c.execute(
            "UPDATE visits SET reception_comment=?, check_out=? WHERE id=?",
            (text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vid)
        )
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ Izoh saqlandi va chat tugatildi.")
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text("Izohni saqlashda xatolik. Qayta urinib ko'ring.")
        return ConversationHandler.END

async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Iltimos, faqat matnli izoh yuboring.")

async def login_reception(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Iltimos: /login <kod>")
        return
    code = context.args[0]
    try:
        conn = sqlite3.connect('kiosk.db')
        c = conn.cursor()
        c.execute('SELECT id, name FROM receptions WHERE login_code=?', (code,))
        row = c.fetchone()
        if not row:
            await update.message.reply_text("Noto'g'ri kod.")
        else:
            rec_id, rec_name = row
            chat_id = update.effective_user.id
            c.execute('UPDATE receptions SET chat_id=? WHERE id=?', (chat_id, rec_id))
            conn.commit()
            await update.message.reply_text(f"✅ {rec_name} login bo'ldi.")
        conn.close()
    except Exception as e:
        await update.message.reply_text("Xatolik yuz berdi. Qayta urinib ko'ring.")

conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(initial_action, pattern=r'^(action_status|finish)\|')],
    states={
        SELECT_STATUS: [CallbackQueryHandler(status_choice, pattern=r'^status_')],
        WAIT_PASSPORT: [MessageHandler(filters.ALL, passport_handler)],
        WAIT_CAR_MODEL: [CallbackQueryHandler(car_model_handler, pattern=r'^car_')],
        WAIT_CAR_COLOR: [CallbackQueryHandler(car_color_handler, pattern=r'^color_')],
        CONFIRM_CONTRACT: [CallbackQueryHandler(confirm_contract_handler, pattern=r'^confirm_contract$')],
        AFTER_STATUS: [
            CallbackQueryHandler(finish_handler, pattern=r'^finish\|'),
            CallbackQueryHandler(comment_request, pattern=r'^comment\|')
        ],
        WAIT_COMMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment),
            MessageHandler(filters.PHOTO | filters.Document.ALL, handle_non_text)
        ]
    },
    fallbacks=[],
)

app.add_handler(conv)
app.add_handler(CommandHandler('login', login_reception))

def start_bot():
    global BOT_LOOP
    BOT_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(BOT_LOOP)
    app.run_polling(stop_signals=())

def stop_bot():
    asyncio.get_event_loop().run_until_complete(app.stop())

if __name__ == '__main__':
    start_bot()
