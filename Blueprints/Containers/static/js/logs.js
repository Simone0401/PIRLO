const logBuffer = {};         // es. logBuffer["pirlo"] = [[timestamp, line], ...]
const lastTimestamp = {};     // es. lastTimestamp["pirlo"] = "2025-06-28T13:20:00"
const logIntervals = {};      // es. logIntervals["pirlo"] = ID setInterval

document.addEventListener("DOMContentLoaded", () => {
    ["pirlo", "tulip", "cannavaro", "totti"].forEach(id => {
  const saved = localStorage.getItem(`logBuffer-${id}`);
  const ts = localStorage.getItem(`lastTimestamp-${id}`);
  if (saved && ts) {
    try {
      logBuffer[id] = JSON.parse(saved);
      lastTimestamp[id] = ts;
    } catch (e) {
      console.warn(`Errore parsing log salvati per ${id}`, e);
    }
  }
});

["pirlo","tulip","cannavaro","totti"].forEach(id => {
      const logBox = document.getElementById(`${id}-log`);
  if (logBox) {
    logBox.addEventListener("scroll", () => {
      const isAtBottom = logBox.scrollTop + logBox.clientHeight >= logBox.scrollHeight - 20;
      if (isAtBottom) {
        const alert = document.getElementById(`${id}-log-alert`);
        if (alert) alert.style.display = "none";
      }
    });
  }

  const alert = document.getElementById(`${id}-log-alert`);
  if (alert) {
    alert.addEventListener("click", () => {
      const logBox = document.getElementById(`${id}-log`);
      if (logBox) logBox.scrollTop = logBox.scrollHeight;
      alert.style.display = "none";
    });
  }
});

});

async function loadLogs(id) {
  try {
    let url = `/containers/api/${id}/logs`;
    if (lastTimestamp[id]) {
      url += `?since=${encodeURIComponent(lastTimestamp[id])}`;
    }
    
    if (logBuffer[id]?.length > 0) {
        showLogsInCard(id, logBuffer[id]);
    }

    const r = await fetch(url);
    const data = await r.json();

    if (data.result) {
      showToast("danger", `Log error: ${data.error}`);
      return;
    }

    if (!logBuffer[id]) logBuffer[id] = [];

    const newEntries = data.logs || [];
    if (newEntries.length > 0) {
      logBuffer[id].push(...newEntries);
      lastTimestamp[id] = newEntries[newEntries.length - 1][0];
    }

    localStorage.setItem(`logBuffer-${id}`, JSON.stringify(logBuffer[id]));
    localStorage.setItem(`lastTimestamp-${id}`, lastTimestamp[id]);

    showLogsInCard(id, logBuffer[id]);

    // 🧠 Se il log è visibile e non è ancora attivo il refresh automatico
    const logBox = document.getElementById(`${id}-log`);
    if (logBox && logBox.style.display === "block" && !logIntervals[id]) {
      logIntervals[id] = setInterval(() => {
        const visible = document.getElementById(`${id}-log`)?.style.display === "block";
        if (visible) {
          loadLogs(id);  // richiama sé stesso
        } else {
          clearInterval(logIntervals[id]);
          delete logIntervals[id];
        }
      }, 5000);
    }
    
  } catch (e) {
    console.error("Errore caricamento log:", e);
    showToast("danger", "Controlla l'endpoint dei log o il server.");
  }
}


function highlightLog(line) {
    return line
        .replace(/\berror\b/gi, '<span style="color:red;font-weight:bold;">$&</span>')
        .replace(/\bwarn\b/gi, '<span style="color:orange;">$&</span>')
        .replace(/\binfo\b/gi, '<span style="color:lightblue;">$&</span>')
        .replace(/\bsuccess\b/gi, '<span style="color:lime;">$&</span>')
        .replace(/\x1b\[[0-9;]*m/g, '');
}

function showLogsInCard(id, entries) {
  const logBox = document.getElementById(`${id}-log`);
  if (!logBox) return;

  logBox.style.display = "block";

  const newHTML = entries.map(([ts, line]) => {
    const safeLine = line
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    return `${highlightLog(safeLine)}`;
  }).join("<br>");

  logBox.innerHTML = newHTML;
  const isAtBottom = logBox.scrollTop + logBox.clientHeight >= logBox.scrollHeight - 20;

  const alertBox = document.getElementById(`${id}-log-alert`);
if (isAtBottom) {
  logBox.innerHTML = newHTML;
  logBox.scrollTop = logBox.scrollHeight;
  if (alertBox) alertBox.style.display = "none";
} else {
  logBox.innerHTML = newHTML;
  if (alertBox) alertBox.style.display = "block";
}

}

function clearLogs(id) {
  delete logBuffer[id];
  delete lastTimestamp[id];
  localStorage.removeItem(`logBuffer-${id}`);
  localStorage.removeItem(`lastTimestamp-${id}`);

  const box = document.getElementById(`${id}-log`);
  if (box) {
    box.innerHTML = "";
    box.style.display = "none";
  }

  showToast("info", `🗑️ Log di ${id} eliminati dal browser`);
}
