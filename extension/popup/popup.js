// ============================================================
// ReplyGenius – Popup Script
// Handles: tab switching, tone selection, settings, saved replies
// ============================================================

const TONES = [
  { id: "normal", emoji: "💬", label: "Normal" }, // NEW
  { id: "casual", emoji: "😊", label: "Casual" },
  { id: "professional", emoji: "💼", label: "Pro" },
  { id: "smart", emoji: "🧠", label: "Smart" },
  { id: "thoughtful", emoji: "💭", label: "Thoughtful" },
  { id: "funny", emoji: "😂", label: "Funny" },
  { id: "genz", emoji: "🔥", label: "Gen Z" },
  { id: "viral", emoji: "⚡", label: "Viral" },
  { id: "deep", emoji: "🌊", label: "Deep" },
];

let settings = {
  backendUrl: "http://localhost:5000",
  defaultTone: "normal", // default to normal — most natural
  defaultLength: "Medium",
  autoInject: true,
};

let savedReplies = [];
let replyCount = 0;

// ── Init ───────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  await loadStoredData();
  renderToneGrid();
  renderSavedReplies();
  updateStats();
  pingBackend();

  // Tab switching
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => switchTab(tab.dataset.tab));
  });

  // Settings save
  document
    .getElementById("saveSettingsBtn")
    .addEventListener("click", saveSettings);

  // Ping backend button
  document.getElementById("pingBtn").addEventListener("click", pingBackend);

  // Settings inputs – pre-populate
  document.getElementById("backendUrlInput").value = settings.backendUrl;
  document.getElementById("defaultLength").value = settings.defaultLength;
  document.getElementById("autoInject").checked = settings.autoInject;
});

// ── Load from chrome.storage ───────────────────────────────────────────────
async function loadStoredData() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(["rgSettings"], (syncResult) => {
      if (syncResult.rgSettings) {
        settings = { ...settings, ...syncResult.rgSettings };
      }
      chrome.storage.local.get(
        ["savedReplies", "replyCount"],
        (localResult) => {
          if (localResult.savedReplies) savedReplies = localResult.savedReplies;
          if (localResult.replyCount) replyCount = localResult.replyCount;
          resolve();
        },
      );
    });
  });
}

// ── Tab Switching ──────────────────────────────────────────────────────────
function switchTab(tabId) {
  document
    .querySelectorAll(".tab")
    .forEach((t) => t.classList.toggle("active", t.dataset.tab === tabId));
  document
    .querySelectorAll(".tab-content")
    .forEach((c) => c.classList.toggle("active", c.id === `tab-${tabId}`));

  if (tabId === "saved") renderSavedReplies();
}

// ── Tone Grid (popup) ──────────────────────────────────────────────────────
function renderToneGrid() {
  const grid = document.getElementById("popupToneGrid");
  grid.innerHTML = TONES.map(
    (t) => `
    <button class="tone-chip-popup ${t.id === settings.defaultTone ? "active" : ""}" data-tone="${t.id}">
      <span class="tone-emoji">${t.emoji}</span>
      ${t.label}
    </button>
  `,
  ).join("");

  grid.querySelectorAll(".tone-chip-popup").forEach((chip) => {
    chip.addEventListener("click", () => {
      grid
        .querySelectorAll(".tone-chip-popup")
        .forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      settings.defaultTone = chip.dataset.tone;
      chrome.storage.sync.set({ rgSettings: settings });
    });
  });
}

// ── Save Settings ──────────────────────────────────────────────────────────
function saveSettings() {
  settings.backendUrl =
    document.getElementById("backendUrlInput").value.trim() ||
    "http://localhost:5000";
  settings.defaultLength = document.getElementById("defaultLength").value;
  settings.autoInject = document.getElementById("autoInject").checked;

  chrome.storage.sync.set({ rgSettings: settings }, () => {
    const toast = document.getElementById("settingsToast");
    toast.style.display = "block";
    setTimeout(() => {
      toast.style.display = "none";
    }, 2500);
    pingBackend();
  });
}

// ── Ping Backend ───────────────────────────────────────────────────────────
async function pingBackend() {
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("backendStatusText");
  statusText.textContent = "Checking...";

  try {
    const res = await fetch(`${settings.backendUrl}/api/health`, {
      signal: AbortSignal.timeout(4000),
    });
    if (res.ok) {
      statusDot.className = "status-dot online";
      statusText.textContent = "✅ Backend connected";
    } else {
      throw new Error("non-ok");
    }
  } catch {
    statusDot.className = "status-dot offline";
    statusText.textContent = "❌ Backend offline";
  }
}

// ── Render Saved Replies ───────────────────────────────────────────────────
function renderSavedReplies() {
  const list = document.getElementById("savedList");

  if (!savedReplies.length) {
    list.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">🔖</span>
        <p>No saved replies yet.</p>
        <small>Click "Save" on any generated reply.</small>
      </div>
    `;
    return;
  }

  list.innerHTML = savedReplies
    .map(
      (r, idx) => `
    <div class="saved-item" data-idx="${idx}">
      <div class="saved-item-meta">
        <span class="saved-tone-badge">${r.tone}</span>
        <span class="saved-platform">${r.platform}</span>
      </div>
      <div class="saved-item-text">${escapeHtml(r.text)}</div>
      <div class="saved-item-actions">
        <button class="saved-copy-btn" data-idx="${idx}">📋 Copy</button>
        <button class="saved-del-btn" data-idx="${idx}">🗑 Delete</button>
      </div>
    </div>
  `,
    )
    .join("");

  list.querySelectorAll(".saved-copy-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const reply = savedReplies[parseInt(btn.dataset.idx)];
      navigator.clipboard.writeText(reply.text);
      btn.textContent = "✅ Copied";
      setTimeout(() => {
        btn.textContent = "📋 Copy";
      }, 1800);
    });
  });

  list.querySelectorAll(".saved-del-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      savedReplies.splice(parseInt(btn.dataset.idx), 1);
      chrome.storage.local.set({ savedReplies });
      renderSavedReplies();
      updateStats();
    });
  });
}

// ── Stats ──────────────────────────────────────────────────────────────────
function updateStats() {
  document.getElementById("statReplies").textContent = replyCount;
  document.getElementById("statSaved").textContent = savedReplies.length;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}
