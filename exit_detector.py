import sqlite3
import cv2
from datetime import datetime
from face_utils import train_recognizer, recognize_label

DB = 'kiosk.db'
PHOTO_DIR = 'photos'
CAMERA_INDEX = 1 

def run():
 
    # train_recognizer(PHOTO_DIR)

   
    # while True:
    #     label = recognize_label(camera_index=CAMERA_INDEX)
    #     if not label:
    #         # hali hech kim aniqlanmadi, yana urinib ko‘ramiz
    #         continue

    #     client_id = int(label)
    #    
    #     conn = sqlite3.connect(DB)
    #     c = conn.cursor()
    #     c.execute('''
    #         SELECT id
    #         FROM visits
    #         WHERE client_id=? AND check_out IS NULL
    #         ORDER BY check_in DESC
    #         LIMIT 1
    #     ''', (client_id,))
    #     row = c.fetchone()
    #     if row:
    #         visit_id = row[0]
    #       
    #         c.execute('''
    #             UPDATE visits
    #             SET check_out=?
    #             WHERE id=?
    #         ''', (datetime.now().isoformat(), visit_id))
    #         conn.commit()
    #     conn.close()
    #     break
    pass
if __name__ == '__main__':
    run()
