document.addEventListener("DOMContentLoaded", () => {
  const actionInProgress = new Set(); // ID dei container con azione in corso

  function showSpinner(id) {
    const title = document.querySelector(`#${id}-title`);
    if (!title || title.querySelector(".spinner")) return;
    const sp = document.createElement("div");
    sp.className = "spinner";
    sp.id = `${id}-spinner`;
    title.appendChild(sp);
  }

  function hideSpinner(id) {
    const sp = document.getElementById(`${id}-spinner`);
    if (sp) sp.remove();
  }

  function disableButtons(id, state) {
    document.querySelectorAll(`[data-container='${id}']`).forEach(btn => {
      btn.disabled = state;
    });
  }


  document.body.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action][data-container]");
    if (!btn) return;

    const action = btn.dataset.action;
    const container = btn.dataset.container;
    let url = `/containers/api/${container}/${action}`;
    const method = (action === "logs") ? "GET" : "POST";

    showSpinner(container);
    disableButtons(container, true);

    try {
      const res = await fetch(url, { method });
      const data = await res.json();

      if (!res.ok || data.result != 0) {
        const msg = data.error || res.statusText || "Errore sconosciuto";
        showToast("danger", `${action.toUpperCase()} fallito: ${msg}`);
        return;
      }

      if (action === "logs") {
        showLogsModal(container, data.logs || "");  // definisci showLogsModal() se vuoi
      } else {
        showToast("success", `${action.toUpperCase()} su ${container}`);
      }

    } catch (err) {
      console.error(err);
      showToast("danger", `❌ Network error: ${err}`);
    } finally {
      hideSpinner(container);
      disableButtons(container, false);
      refreshAll();
    }
  });
});