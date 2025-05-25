import cv2, os, numpy as np

CASCADE    = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()

def train_recognizer(photo_dir='photos'):
    imgs, labels = [], []
    for fn in os.listdir(photo_dir):
        if not fn.lower().endswith('.jpg'): continue
        gray = cv2.imread(os.path.join(photo_dir, fn), cv2.IMREAD_GRAYSCALE)
        faces = CASCADE.detectMultiScale(gray, 1.1, 4)
        if len(faces) != 1: continue
        x,y,w,h = faces[0]
        imgs.append(gray[y:y+h, x:x+w])
        labels.append(int(os.path.splitext(fn)[0]))  # filename = PHONE label
    if imgs:
        RECOGNIZER.train(imgs, np.array(labels))

def capture_and_register(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    cap.release()
    if not ret: raise RuntimeError("Kameradan surat olinmadi")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = CASCADE.detectMultiScale(gray, 1.1, 4)
    if len(faces) != 1:
        raise RuntimeError("Iltimos, faqat bitta yuz bilan surat oling")
    x,y,w,h = faces[0]
    return frame, gray[y:y+h, x:x+w]

def recognize_label(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    cap.release()
    if not ret: return None
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = CASCADE.detectMultiScale(gray, 1.1, 4)
    if len(faces) != 1: return None
    x,y,w,h = faces[0]
    label, conf = RECOGNIZER.predict(gray[y:y+h, x:x+w])
    return str(label) if conf < 80 else None
