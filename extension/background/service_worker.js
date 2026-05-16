// ============================================================
// ReplyGenius – Background Service Worker
// Handles messages from content scripts and popup.
// Acts as the bridge between the extension UI and Flask backend.
// ============================================================

// Default backend URL – user can override this in settings
const DEFAULT_BACKEND = "https://replygenius-a92f.onrender.com"; 

// ── Listen for messages from content scripts or popup ──────────────────────
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GENERATE_REPLY") {
    handleGenerateReply(message.payload)
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message }));

    // Return true to keep the message channel open for async response
    return true;
  }

  if (message.type === "GET_BACKEND_URL") {
    getBackendUrl().then((url) => sendResponse({ url }));
    return true;
  }
});

// ── Fetch backend URL from storage (user can change it in popup) ───────────
async function getBackendUrl() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(["backendUrl"], (result) => {
      resolve(result.backendUrl || DEFAULT_BACKEND);
    });
  });
}

// ── Main: send post text + tone to Flask backend ───────────────────────────
async function handleGenerateReply({ postText, tone, platform, length }) {
  const backendUrl = await getBackendUrl();

  const response = await fetch(`${backendUrl}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ postText, tone, platform, length }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.error || `Server error: ${response.status}`);
  }

  return response.json();
}
