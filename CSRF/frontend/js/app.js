(() => {
  const notice = document.getElementById("notice");
  let csrfToken = "";

  function showNotice(message, kind = "danger") {
    if (!notice) return;
    notice.className = `alert alert-${kind}`;
    notice.textContent = message;
  }

  async function api(url, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body) headers.set("Content-Type", "application/json");
    if (csrfToken && options.method && options.method !== "GET") {
      headers.set("X-CSRF-Token", csrfToken);
    }
    const response = await fetch(url, { ...options, headers, credentials: "same-origin" });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || "The request could not be completed.");
    return body;
  }

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = new FormData(loginForm);
      try {
        await api("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ username: data.get("username"), password: data.get("password") }),
        });
        window.location.assign("/");
      } catch (error) {
        showNotice(error.message);
      }
    });
  }

  const transferForm = document.getElementById("transfer-form");
  if (!transferForm) return;

  function formatMoney(paise) {
    return new Intl.NumberFormat("en-IN", {
      style: "currency", currency: "INR", minimumFractionDigits: 2,
    }).format(paise / 100);
  }

  function formatDate(value) {
    return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  }

  async function loadDashboard() {
    try {
      const [identity, account, transactions] = await Promise.all([
        api("/api/auth/me"),
        api("/api/account"),
        api("/api/transactions"),
      ]);
      csrfToken = identity.csrf_token;
      document.getElementById("nav-username").textContent = account.username;
      document.getElementById("account-name").textContent = account.username;
      document.getElementById("balance").textContent = formatMoney(account.balance_paise);
      const body = document.getElementById("transactions");
      document.getElementById("transaction-count").textContent = `${transactions.length} record${transactions.length === 1 ? "" : "s"}`;
      if (!transactions.length) {
        body.innerHTML = '<tr><td colspan="4" class="text-center text-secondary py-4">No transactions yet.</td></tr>';
        return;
      }
      body.replaceChildren(...transactions.map((transaction) => {
        const row = document.createElement("tr");
        const activity = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = `direction-badge${transaction.direction === "received" ? " received" : ""}`;
        badge.textContent = transaction.direction;
        activity.append(badge);
        const other = document.createElement("td");
        other.textContent = transaction.other_party;
        const date = document.createElement("td");
        date.className = "text-secondary";
        date.textContent = formatDate(transaction.created_at);
        const amount = document.createElement("td");
        amount.className = `text-end fw-semibold${transaction.direction === "received" ? " text-success" : ""}`;
        amount.textContent = `${transaction.direction === "sent" ? "−" : "+"}${formatMoney(transaction.amount_paise)}`;
        row.append(activity, other, date, amount);
        return row;
      }));
    } catch (error) {
      if (error.message.includes("log in") || error.message.includes("Not authenticated")) {
        window.location.assign("/login");
        return;
      }
      showNotice(error.message);
    }
  }

  transferForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = document.getElementById("transfer-button");
    button.disabled = true;
    const data = new FormData(transferForm);
    try {
      const result = await api("/transfer", {
        method: "POST",
        body: JSON.stringify({ recipient: data.get("recipient"), amount: data.get("amount") }),
      });
      showNotice(`Transfer of ${formatMoney(result.amount_paise)} to ${result.recipient} completed.`, "success");
      transferForm.reset();
      await loadDashboard();
    } catch (error) {
      showNotice(error.message);
    } finally {
      button.disabled = false;
    }
  });

  document.getElementById("logout-button").addEventListener("click", async () => {
    try {
      await api("/api/auth/logout", { method: "POST", body: "{}" });
      window.location.assign("/login");
    } catch (error) {
      showNotice(error.message);
    }
  });

  loadDashboard();
})();
