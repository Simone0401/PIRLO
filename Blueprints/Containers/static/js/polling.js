async function refreshAll() {
  try {
    const r = await fetch("/containers/api/all-status");
    const statuses = await r.json();
    for (const [id, status] of Object.entries(statuses)) {
      const b = document.getElementById(`${id}-status`);
      b.textContent = status.charAt(0).toUpperCase() + status.slice(1);
      b.classList.toggle("bg-success", status === "running");
      b.classList.toggle("bg-danger",  status !== "running");
    }
  } catch (e) {
    console.error("Errore aggiornamento status:", e);
  }
}

setInterval(refreshAll, 10000);
refreshAll();  // prima lettura
