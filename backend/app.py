from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import sqlite3
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# Load model
model = pickle.load(open("model/model.pkl", "rb"))
tfidf = pickle.load(open("model/tfidf.pkl", "rb"))

DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            result TEXT,
            confidence REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def serve_frontend():
    return send_from_directory("static", "index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    vec = tfidf.transform([text])
    proba = model.predict_proba(vec)[0]
    pred = model.predict(vec)[0]

    label = "REAL ✅" if pred == 1 else "FAKE ❌"
    confidence = float(max(proba)) * 100

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO predictions (text, result, confidence) VALUES (?, ?, ?)",
              (text, label, confidence))
    conn.commit()
    conn.close()

    return jsonify({
        "prediction": label,
        "confidence": round(confidence, 2)
    })

@app.route("/history")
def history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT result, confidence FROM predictions ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)