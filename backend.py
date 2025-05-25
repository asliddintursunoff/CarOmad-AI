# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sqlite3
import pandas as pd
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from fastapi.responses import JSONResponse

DB = "kiosk.db"
MODEL_PATH = "ml_model.pkl"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

def train_and_save_model():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query('''
        SELECT v.*, c.age, c.gender FROM visits v
        JOIN clients c ON v.client_id = c.id
    ''', conn)
    if df.empty: return False
    df['check_in'] = pd.to_datetime(df['check_in'])
    df['check_out'] = pd.to_datetime(df['check_out'])
    df['duration'] = (df['check_out'] - df['check_in']).dt.total_seconds() / 60
    agg = df.groupby('client_id').agg({
        'age': 'first', 'gender': 'first', 'id': 'count',
        'duration': 'mean', 'service': lambda x: (x == 'test-drive').sum(),
        'status': lambda x: (x == 'purchased').any()
    })
    agg = agg.rename(columns={'id': 'visits', 'duration': 'avg_time', 'service': 'test_drive_count', 'status': 'purchased'})
    agg['purchased'] = agg['purchased'].astype(int)
    agg['gender'] = agg['gender'].map({'male': 1, 'female': 0})
    features = ['age', 'gender', 'visits', 'avg_time', 'test_drive_count']
    X = agg[features].fillna(0)
    y = agg['purchased']
    if y.sum() == 0 or y.sum() == len(y): return False
    model = LogisticRegression()
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return True

def load_model():
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        return None

@app.get("/api/clients")
def api_clients():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, name, age, gender, phone, photo_path FROM clients ORDER BY id')
    rows = c.fetchall()
    conn.close()
    return [
        dict(zip(['id', 'name', 'age', 'gender', 'phone', 'photo'], row))
        for row in rows
    ]

@app.get("/api/potential_buyers_ml")
def potential_buyers_ml():
    model = load_model()
    if model is None: return []
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query('''
        SELECT v.*, c.age, c.gender, c.name, c.last_name FROM visits v
        JOIN clients c ON v.client_id = c.id
        WHERE v.status IS NULL OR v.status != "purchased"
    ''', conn)
    if df.empty: return []
    df['check_in'] = pd.to_datetime(df['check_in'])
    df['check_out'] = pd.to_datetime(df['check_out'])
    df['duration'] = (df['check_out'] - df['check_in']).dt.total_seconds() / 60
    buyers = []
    for client_id, group in df.groupby('client_id'):
        age = int(group['age'].iloc[0])
        gender = str(group['gender'].iloc[0])
        name = str(group['name'].iloc[0])
        last_name = str(group['last_name'].iloc[0])
        visits = int(len(group))
        avg_time = float(group['duration'].mean())
        test_drive_count = int((group['service'] == 'test-drive').sum())
        gender_num = 1 if gender == "male" else 0
        features = np.array([[age, gender_num, visits, avg_time, test_drive_count]])
        proba = float(model.predict_proba(features)[0,1])
        buyers.append({
            "client_id": int(client_id),
            "name": name,
            "last_name": last_name,
            "age": age,
            "gender": gender,
            "visits": visits,
            "avg_time": round(avg_time, 1),
            "test_drive_count": test_drive_count,
            "probability": round(proba * 100, 2)
        })
    buyers = sorted(buyers, key=lambda x: x['probability'], reverse=True)
    return buyers

@app.post("/api/retrain_model")
def retrain_model():
    success = train_and_save_model()
    return {"success": bool(success)}

@app.get("/api/stats")
def api_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
      SELECT
        v.id, c.name, c.age, c.photo_path,
        v.check_in, v.check_out, v.service,
        v.reception_comment, v.visit_token
      FROM visits v
      JOIN clients c ON c.id = v.client_id
      ORDER BY v.check_in DESC
    ''')
    rows = c.fetchall()
    conn.close()
    records = []
    service_counts = {}
    hours_set = set()
    for row in rows:
        ci = row[4]
        co = row[5]
        duration = '—'
        if co:
            try:
                from datetime import datetime
                dt_in  = datetime.fromisoformat(ci)
                dt_out = datetime.fromisoformat(co)
                duration = str(dt_out - dt_in).split('.')[0]
            except: pass
        service = row[6]
        service_counts[service] = service_counts.get(service, 0) + 1
        try:
            hr = int(ci[11:13])
            hours_set.add(hr)
        except: pass
        records.append({
            'id':      row[0],
            'name':    row[1],
            'age':     row[2],
            'photo':   row[3],
            'check_in':ci,
            'check_out': co or '—',
            'duration': duration,
            'service': service,
            'comment': row[7] or '—',
            'token':   row[8]
        })
    hours = sorted(hours_set)
    return JSONResponse(content={
        "records": records,
        "service_stats": service_counts,
        "hours": hours
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
