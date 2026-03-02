import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# ✅ Load dataset
if os.path.exists("news.csv"):
    df = pd.read_csv("news.csv")
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("news.csv must contain columns: text, label")
    df = df[["text", "label"]]
else:
    if not (os.path.exists("Fake.csv") and os.path.exists("True.csv")):
        raise FileNotFoundError("Put either news.csv OR both Fake.csv and True.csv inside backend folder")

    fake = pd.read_csv("Fake.csv")
    true = pd.read_csv("True.csv")

    if "text" not in fake.columns or "text" not in true.columns:
        raise ValueError("Fake.csv and True.csv must have a 'text' column")

    fake["label"] = "FAKE"
    true["label"] = "REAL"
    df = pd.concat([fake[["text", "label"]], true[["text", "label"]]], ignore_index=True)

# ✅ Clean
df["text"] = df["text"].astype(str).fillna("").str.strip()
df["label"] = df["label"].astype(str).str.upper().str.strip()

# ✅ Map labels to numbers
df["label"] = df["label"].map({"FAKE": 0, "REAL": 1})
df = df.dropna(subset=["label"])

# ✅ Safe split (works even for tiny datasets)
if len(df) < 20:
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.5, random_state=42
    )
else:
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

# ✅ TF-IDF
tfidf = TfidfVectorizer(stop_words="english", max_df=0.7)
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

# ✅ Model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# ✅ Evaluate
pred = model.predict(X_test_vec)
acc = accuracy_score(y_test, pred)

# ✅ Save
os.makedirs("model", exist_ok=True)

with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("model/tfidf.pkl", "wb") as f:
    pickle.dump(tfidf, f)

print("✅ Training complete!")
print("✅ Accuracy:", round(acc * 100, 2), "%")
print("✅ Saved: model/model.pkl and model/tfidf.pkl")