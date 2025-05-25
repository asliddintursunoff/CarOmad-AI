import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2, sqlite3, os
from datetime import datetime

from bot import assign_reception_and_notify
from face_utils import train_recognizer, CASCADE, RECOGNIZER

DB = 'kiosk.db'
PHOTO_DIR = 'photos'
os.makedirs(PHOTO_DIR, exist_ok=True)

# --- Supported languages and translations ---
LANGS = ['uz', 'ru', 'en']
LANG_LABELS = {'uz': "O‘zbekcha", 'ru': "Русский", 'en': "English"}
T = {
    'title': {'uz': "Avtosalon Kiosk", 'ru': "Киоск автосалона", 'en': "Car Dealer Kiosk"},
    'register': {'uz': "Ro‘yxatdan o‘tish", 'ru': "Регистрация", 'en': "Register"},
    'services': {'uz': "Xizmatlar", 'ru': "Услуги", 'en': "Services"},
    'service_choose': {'uz': "Xizmatni tanlang", 'ru': "Выберите услугу", 'en': "Select a Service"},
    'back': {'uz': "🔙 Orqaga", 'ru': "🔙 Назад", 'en': "🔙 Back"},
    'scan_face': {'uz': "🔍 Yuzni aniqlash", 'ru': "🔍 Сканировать лицо", 'en': "🔍 Scan Face"},
    'face_login': {'uz': "Xizmat uchun Face-Login", 'ru': "Вход по лицу для услуги", 'en': "Face-Login for Services"},
    'thanks': {'uz': "Rahmat!", 'ru': "Спасибо!", 'en': "Thank you!"},
    'service': {'uz': "Xizmat", 'ru': "Услуга", 'en': "Service"},
    'queue': {'uz': "Navbat raqami", 'ru': "Номер очереди", 'en': "Queue number"},
    'not_registered': {'uz': "Hech kim ro‘yxatdan o‘tmagan.", 'ru': "Нет зарегистрированных.", 'en': "No one registered yet."},
    'face_not_recognized': {'uz': "Yuz tanilmadi.", 'ru': "Лицо не распознано.", 'en': "Face not recognized."},
}

SERVICES = {
    'uz': [("Test drive", "Test drive"), ("Ko‘rik", "Ko‘rik"), ("Sotib olish", "Sotib olish")],
    'ru': [("Тест-драйв", "Test drive"), ("Осмотр", "Ko‘rik"), ("Покупка", "Sotib olish")],
    'en': [("Test drive", "Test drive"), ("Inspection", "Ko‘rik"), ("Purchase", "Sotib olish")],
}

# --- DB migration for last_name column (safe) ---
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("PRAGMA table_info(clients)")
cols = [row[1] for row in c.fetchall()]
if 'last_name' not in cols:
    c.execute("ALTER TABLE clients ADD COLUMN last_name TEXT")
    conn.commit()
conn.close()

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg="#F28C38", fg="white", width=450, height=80):
        super().__init__(parent, width=width, height=height, bg="#2E2E2E", highlightthickness=0)
        self.command = command
        self.bg = bg
        self.fg = fg
        self.width = width
        self.height = height
        radius = min(width, height) * 0.25
        self.create_rounded_rect(5, 5, width-5, height-5, radius, fill=bg, outline=bg)
        self.create_text(width/2, height/2, text=text, fill=fg, font=("Segoe UI", 18), anchor="center")  # Increased font size
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.itemconfig(1, fill="#D66D1E", outline="#D66D1E"))
        self.bind("<Leave>", lambda e: self.itemconfig(1, fill=bg, outline=bg))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

class CameraWindow:
    def __init__(self, parent, on_close):
        self.parent = parent
        self.on_close = on_close
        self.last_frame = None
        self.cropped = None

        # Clear the parent window and add camera widgets
        self.parent.clear()
        self.lbl = tk.Label(self.parent, bg="#2E2E2E", bd=1, relief="solid", highlightthickness=1, highlightbackground="#444")
        self.lbl.pack(padx=15, pady=15)

        btnf = tk.Frame(self.parent, bg="#2E2E2E")
        btnf.pack(pady=10)
        RoundedButton(btnf, text="📸 Capture", command=self.capture, width=300, height=80).pack(side="left", padx=10)
        RoundedButton(btnf, text="❌ Cancel", command=self.close, bg="#D32F2F", width=300, height=80).pack(side="left", padx=10)

        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update()

    def update(self):
        if not self.running:
            return
        ret, frame = self.cap.read()
        if ret:
            h, w = frame.shape[:2]
            x1, y1 = int(w*0.3), int(h*0.2)
            x2, y2 = int(w*0.7), int(h*0.8)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            self.last_frame = frame
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(img))
            self.lbl.imgtk = img
            self.lbl.configure(image=img)
        self.parent.after(30, self.update)

    def capture(self):
        if self.last_frame is None:
            messagebox.showerror("Error", "No camera frame.")
            return
        gray = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2GRAY)
        faces = CASCADE.detectMultiScale(gray, 1.1, 4)
        if len(faces) != 1:
            messagebox.showerror("Error", "Align exactly one face.")
            return
        x, y, w, h = faces[0]
        self.cropped = gray[y:y+h, x:x+w]
        self.close()

    def close(self):
        self.running = False
        self.cap.release()
        self.on_close(self.cropped)

def open_camera(parent, on_close):
    win = CameraWindow(parent, on_close)
    return win.cropped

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Avtosalon Kiosk")
        self.lang = None
        self.configure(bg="#2E2E2E")
        self.geometry("754x942")  # Fixed size
        self._choose_language()
        self.camera_result = None
        self.previous_screen = None

    def t(self, key):
        return T.get(key, {}).get(self.lang, "") if self.lang else ""

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def _btn(self, text, cmd):
        return RoundedButton(self, text=text, command=cmd, width=450, height=80)

    def _choose_language(self):
        self.clear()
        self.lang = None
        tk.Label(self, text="Choose language / Tilni tanlang / Выберите язык",
                 bg="#2E2E2E", font=("Segoe UI", 18, "bold"), fg="#F28C38").pack(pady=50)
        for code in LANGS:
            RoundedButton(self, text=LANG_LABELS[code], command=lambda c=code: self._set_lang(c),
                          width=350, height=80).pack(pady=25)

    def _set_lang(self, lang_code):
        self.lang = lang_code
        self._main_menu()

    def _main_menu(self):
        self.clear()
        tk.Label(self, text=self.t('title'), bg="#2E2E2E",
                 font=("Segoe UI", 20, "bold"), fg="#F28C38").pack(pady=50)
        self._btn(f"1 ▶ {self.t('register')}", self._show_register).pack(pady=25)
        self._btn(f"2 ▶ {self.t('services')}", self._show_login).pack(pady=25)
        self._btn("🌐 Change Language", self._choose_language).pack(pady=25)

    def _show_register(self):
        self.clear()
        tk.Label(self, text=self.t('register'), bg="#2E2E2E",
                 font=("Segoe UI", 18, "bold"), fg="#F28C38").pack(pady=20)
        self._field("Ism:", "name_entry")
        self._field("Familiya:", "last_name_entry")
        self._field("Yosh:", "age_entry")
        tk.Label(self, text="Jins:", bg="#2E2E2E", font=("Segoe UI", 12), fg="#FFF").pack(pady=(15,0))
        self.gender = tk.StringVar(value="Erkak")
        opt = tk.OptionMenu(self, self.gender, "Erkak", "Ayol")
        opt.config(bg="#444", fg="#FFF", font=("Segoe UI", 12), width=15, relief="solid", bd=1)
        opt.pack(pady=5)
        self._field("Telefon:", "phone_entry")
        self._btn("📸 Take Photo & Register", self.do_register).pack(pady=25)
        self._btn(self.t('back'), self._main_menu).pack(pady=25)

    def _field(self, label, attr):
        tk.Label(self, text=label, bg="#2E2E2E", font=("Segoe UI", 12), fg="#FFF").pack(pady=(15,0))
        ent = tk.Entry(self, bg="#444", fg="#FFF", font=("Segoe UI", 12),
                       relief="solid", bd=1, highlightthickness=1, highlightbackground="#555", width=25)
        ent.pack(pady=5, padx=10)
        setattr(self, attr, ent)

    def do_register(self):
        name = self.name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        age_s = self.age_entry.get().strip()
        phone = self.phone_entry.get().strip()
        if not name or not last_name:
            messagebox.showwarning("Xatolik", "Ism va familiya kiritilishi shart.")
            return
        try:
            age = int(age_s)
        except:
            messagebox.showwarning("Xatolik", "Yosh raqam bo‘lishi kerak.")
            return
        if not phone:
            messagebox.showwarning("Xatolik", "Telefon raqamni kiriting.")
            return

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('''
          INSERT INTO clients(name, last_name, age, gender, phone)
          VALUES(?,?,?,?,?)
        ''', (name, last_name, age, self.gender.get(), phone))
        client_id = c.lastrowid
        conn.commit()
        conn.close()

        self.previous_screen = self._show_register
        self.camera_result = None
        def on_camera_close(result):
            self.camera_result = result
            self.previous_screen()
            self._process_register_result(client_id)

        open_camera(self, on_camera_close)

    def _process_register_result(self, client_id):
        crop = self.camera_result
        if crop is None:
            return
        path = os.path.join(PHOTO_DIR, f"{client_id}.jpg")
        cv2.imwrite(path, crop)

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('UPDATE clients SET photo_path=? WHERE id=?', (path, client_id))
        conn.commit(); conn.close()

        messagebox.showinfo("OK", "Ro‘yxatdan muvaffaqiyatli bajarildi.")
        self._choose_language()

    def _show_login(self):
        self.clear()
        tk.Label(self, text=self.t('face_login'), bg="#2E2E2E",
                 font=("Segoe UI", 18, "bold"), fg="#F28C38").pack(pady=30)
        self._btn(self.t('scan_face'), self._auth).pack(pady=25)
        self._btn(self.t('back'), self._main_menu).pack(pady=25)

    def _auth(self):
        photos = os.listdir(PHOTO_DIR)
        if not photos:
            messagebox.showwarning("!", self.t('not_registered'))
            return
        train_recognizer(PHOTO_DIR)

        self.previous_screen = self._show_login
        self.camera_result = None
        def on_camera_close(result):
            self.camera_result = result
            self.previous_screen()
            self._process_auth_result()

        open_camera(self, on_camera_close)

    def _process_auth_result(self):
        crop = self.camera_result
        if crop is None:
            return
        try:
            label, conf = RECOGNIZER.predict(crop)
        except cv2.error:
            messagebox.showerror("Xatolik", "Face recognition not ready.")
            return
        if conf > 80:
            messagebox.showwarning("!", self.t('face_not_recognized'))
            return
        self.client_id = int(label)
        self._show_services()

    def _show_services(self):
        self.clear()
        tk.Label(self, text=self.t('service_choose'), bg="#2E2E2E",
                 font=("Segoe UI", 18, "bold"), fg="#F28C38").pack(pady=30)
        for btn_text, uzbek_xizmat in SERVICES[self.lang]:
            self._btn(btn_text, lambda s=uzbek_xizmat: self._start_service(s)).pack(pady=25)
        self._btn(self.t('back'), self._main_menu).pack(pady=25)

    def _start_service(self, purpose_uzbek):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('INSERT INTO visits(client_id, check_in, service) VALUES(?,?,?)',
                  (self.client_id, now, purpose_uzbek))
        visit_id = c.lastrowid
        conn.commit(); conn.close()
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('SELECT name, last_name FROM clients WHERE id=?', (self.client_id,))
        row = c.fetchone(); conn.close()
        client_name = f"{row[0]} {row[1]}" if row else ''
        assign_reception_and_notify(self.client_id, client_name, purpose_uzbek, visit_id)
        messagebox.showinfo(self.t('thanks'), f"{self.t('service')}: {purpose_uzbek}\n{self.t('queue')}: {visit_id}")
        self._choose_language()

if __name__ == "__main__":
    App().mainloop()