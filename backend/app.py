from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import sqlite3
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# ✅ Load model
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
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()

        if not text:
            return jsonify({"error": "Please paste news text"}), 400

        vec = tfidf.transform([text])
        proba = model.predict_proba(vec)[0]
        pred = int(model.predict(vec)[0])

        label = "REAL ✅" if pred == 1 else "FAKE ❌"
        confidence = float(max(proba)) * 100

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute(
            "INSERT INTO predictions (text, result, confidence) VALUES (?, ?, ?)",
            (text, label, confidence)
        )
        conn.commit()
        conn.close()

        return jsonify({"prediction": label, "confidence": round(confidence, 2)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, result, confidence FROM predictions ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)