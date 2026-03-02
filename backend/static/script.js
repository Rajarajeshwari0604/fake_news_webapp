const API = ""; // same server (Flask)

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn");
  if (btn) btn.addEventListener("click", checkNews);
  loadHistory();
});

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
    resultBox.innerHTML = "❗ Backend not reachable. Please restart Flask server.";
  }
}

async function loadHistory() {
  const historyBox = document.getElementById("history");

  try {
    const res = await fetch(`${API}/history`);
    const data = await res.json();

    let html = "<h3>Last 10 Predictions</h3><ul>";
    data.forEach(row => {
      // row = [id, result, confidence] OR [result, confidence]
      const result = row[1] ?? row[0];
      const conf = row[2] ?? row[1];
      html += `<li>${result} - ${conf}%</li>`;
    });
    html += "</ul>";

    historyBox.innerHTML = html;
  } catch {
    historyBox.innerHTML = "";
  }
}