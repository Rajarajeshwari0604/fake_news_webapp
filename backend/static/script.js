const API = "";

document.getElementById("btn").addEventListener("click", checkNews);

async function checkNews() {
  const text = document.getElementById("news").value.trim();
  const resultBox = document.getElementById("result");

  if (!text) {
    resultBox.innerHTML = "❗ Please paste some news text.";
    return;
  }

  resultBox.innerHTML = "⏳ Checking...";

  try {
    const res = await fetch(`${API}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    if (!res.ok) {
      resultBox.innerHTML = `❗ ${data.error || "Server error"}`;
      return;
    }

    resultBox.innerHTML =
      `Result: ${data.prediction}<br><small>Confidence: ${data.confidence}%</small>`;

    loadHistory();
  } catch (err) {
    resultBox.innerHTML =
      "❗ Cannot connect to backend. Make sure backend is running on http://127.0.0.1:5000";
  }
}

async function loadHistory() {
  const historyBox = document.getElementById("history");

  try {
    const res = await fetch(`${API}/history`);
    const data = await res.json();

    let html = "<h3>Last 10 Predictions</h3><ul>";
    data.forEach(row => {
      html += `<li>${row[1]} - ${row[2]}%</li>`;
    });
    html += "</ul>";

    historyBox.innerHTML = html;
  } catch {
    historyBox.innerHTML = "";
  }
}

loadHistory();