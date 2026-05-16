// ============================================================
// ReplyGenius – Content Script
// This script runs on LinkedIn, X, Reddit, and Medium.
// It detects posts and injects the "✨ Generate Reply" button.
// ============================================================

// ── Platform detection ─────────────────────────────────────────────────────
const PLATFORM = detectPlatform();

function detectPlatform() {
  const host = window.location.hostname;
  if (host.includes("linkedin.com")) return "linkedin";
  if (host.includes("twitter.com") || host.includes("x.com")) return "twitter";
  if (host.includes("reddit.com")) return "reddit";
  if (host.includes("medium.com")) return "medium";
  return "unknown";
}

// ── Platform-specific selectors ────────────────────────────────────────────
// Each platform has different HTML structure, so we target differently.
const SELECTORS = {
  linkedin: {
    // Broadened selectors to handle LinkedIn DOM variations and SPA updates
    feed: "div[data-urn^='urn:li:activity:'], article, .feed-shared-update-v2, .occludable-update, .update",
    text: ".feed-shared-text, .feed-shared-update-v2__description, .attributed-text-segment-list__content, .update-components-text, span.break-words, div.break-words",
    actions:
      ".social-actions-bar, .feed-shared-social-actions, [data-test-social-actions], [data-control-name='comments'], [role='group']",
  },
  twitter: {
    feed: "article[data-testid='tweet']",
    text: "[data-testid='tweetText']",
    actions: "[role='group'][id^='id__']",
  },
  reddit: {
    feed: "[data-testid='post-container'], .Post, shreddit-post",
    text: "[data-click-id='text'] .RichTextJSON-root, .md, [slot='text-body']",
    actions: ".action-buttons, [data-click-id='body']",
  },
  medium: {
    feed: "article",
    text: "article p, .graf--p",
    actions: ".js-postActionsPanel, .postActions, footer",
  },
};

// ── Tones available for the user to select ─────────────────────────────────
const TONES = [
  { id: "normal", label: "💬 Normal" }, // NEW – simple everyday english
  { id: "casual", label: "😊 Casual" },
  { id: "professional", label: "💼 Professional" },
  { id: "smart", label: "🧠 Smart" },
  { id: "thoughtful", label: "💭 Thoughtful" },
  { id: "funny", label: "😂 Funny" },
  { id: "genz", label: "🔥 Gen Z" },
  { id: "viral", label: "⚡ Viral" },
  { id: "deep", label: "🌊 Deep" },
];

const LENGTHS = ["Short", "Medium", "Long"];

// ── State for saved replies ─────────────────────────────────────────────────
let savedReplies = [];
chrome.storage.local.get(["savedReplies"], (r) => {
  if (r.savedReplies) savedReplies = r.savedReplies;
});

// ── Inject buttons into all detected posts ─────────────────────────────────
function injectButtons() {
  const sel = SELECTORS[PLATFORM];
  if (!sel) return;

  const posts = document.querySelectorAll(sel.feed);

  posts.forEach((post) => {
    // Skip if already injected
    if (post.querySelector(".rg-btn")) return;

    // Extract post text
    const textEl = post.querySelector(sel.text);
    const postText = textEl ? textEl.innerText.trim() : "";
    if (!postText || postText.length < 20) return; // skip very short / empty

    // Find actions bar to append button to
    const actionsBar = post.querySelector(sel.actions);
    if (!actionsBar && PLATFORM !== "medium") return;

    // Create the button
    const btn = createGenerateButton(post, postText, actionsBar || post);
    const target = actionsBar || post;
    target.appendChild(btn);
  });
}

// ── Create the ✨ Generate Reply button ─────────────────────────────────────
function createGenerateButton(post, postText, attachTarget) {
  const btn = document.createElement("button");
  btn.className = "rg-btn";
  btn.innerHTML = `<span class="rg-btn-icon">✨</span> Generate Reply`;

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    e.preventDefault();

    // Toggle panel
    const existingPanel = post.querySelector(".rg-panel");
    if (existingPanel) {
      existingPanel.remove();
      return;
    }

    const panel = createReplyPanel(postText, post);
    // Insert panel after the actions bar or after the button
    attachTarget.insertAdjacentElement("afterend", panel);
  });

  return btn;
}

// ── Build the reply panel UI ────────────────────────────────────────────────
function createReplyPanel(postText, postEl) {
  // State
  let selectedTone = "normal"; // default to normal — most natural sounding
  let selectedLength = "Medium";
  let currentReply = "";

  // ── Root panel ─────────────────────────────────────────────
  const panel = document.createElement("div");
  panel.className = "rg-panel";

  // ── Header ─────────────────────────────────────────────────
  panel.innerHTML = `
    <div class="rg-panel-header">
      <div class="rg-panel-title">
        <span class="rg-logo-dot"></span>
        ReplyGenius
      </div>
      <button class="rg-close-btn" title="Close">✕</button>
    </div>

    <div class="rg-tones">
      ${TONES.map(
        (t) =>
          `<button class="rg-tone-chip ${t.id === selectedTone ? "rg-active" : ""}" data-tone="${t.id}">
          ${t.label}
        </button>`,
      ).join("")}
    </div>

    <div class="rg-length-row">
      <span>Length:</span>
      <div class="rg-length-btns">
        ${LENGTHS.map(
          (l) =>
            `<button class="rg-len-btn ${l === selectedLength ? "rg-active" : ""}" data-len="${l}">${l}</button>`,
        ).join("")}
      </div>
    </div>

    <button class="rg-generate-btn">✨ Generate Reply</button>

    <div class="rg-output-area"></div>
  `;

  // ── Close button ────────────────────────────────────────────
  panel.querySelector(".rg-close-btn").addEventListener("click", () => {
    panel.remove();
  });

  // ── Tone chips ──────────────────────────────────────────────
  panel.querySelectorAll(".rg-tone-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      panel
        .querySelectorAll(".rg-tone-chip")
        .forEach((c) => c.classList.remove("rg-active"));
      chip.classList.add("rg-active");
      selectedTone = chip.dataset.tone;
    });
  });

  // ── Length buttons ──────────────────────────────────────────
  panel.querySelectorAll(".rg-len-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      panel
        .querySelectorAll(".rg-len-btn")
        .forEach((b) => b.classList.remove("rg-active"));
      btn.classList.add("rg-active");
      selectedLength = btn.dataset.len;
    });
  });

  // ── Generate button ─────────────────────────────────────────
  const generateBtn = panel.querySelector(".rg-generate-btn");
  const outputArea = panel.querySelector(".rg-output-area");

  generateBtn.addEventListener("click", async () => {
    generateBtn.disabled = true;
    generateBtn.textContent = "Generating...";

    // Show loading state
    outputArea.innerHTML = `
      <div class="rg-loading">
        <div class="rg-spinner"></div>
        <div class="rg-loading-dots">
          <span>·</span><span>·</span><span>·</span>
        </div>
        <span>Crafting your reply</span>
      </div>
    `;

    try {
      // Send to background service worker → Flask backend
      const result = await sendMessage({
        type: "GENERATE_REPLY",
        payload: {
          postText: postText.slice(0, 1500), // cap to avoid huge payloads
          tone: selectedTone,
          platform: PLATFORM,
          length: selectedLength,
        },
      });

      if (!result.success) throw new Error(result.error);

      currentReply = result.data.reply;
      renderReply(outputArea, currentReply);
    } catch (err) {
      outputArea.innerHTML = `
        <div class="rg-error">
          ⚠️ ${escapeHtml(err.message || "Something went wrong. Is the backend running?")}
        </div>
      `;
    } finally {
      generateBtn.disabled = false;
      generateBtn.innerHTML = "✨ Regenerate";
    }
  });

  return panel;

  // ── Helpers ──────────────────────────────────────────────────

  function renderReply(container, text) {
    container.innerHTML = `
      <div class="rg-reply-container">
        <p class="rg-reply-text">${escapeHtml(text)}</p>
      </div>
      <div class="rg-actions">
        <button class="rg-action-btn rg-copy-btn">📋 Copy</button>
        <button class="rg-action-btn rg-save-btn">🔖 Save</button>
        <button class="rg-action-btn rg-regen-btn">🔄 Regenerate</button>
      </div>
    `;

    // Copy button
    container.querySelector(".rg-copy-btn").addEventListener("click", () => {
      navigator.clipboard.writeText(text).then(() => {
        const btn = container.querySelector(".rg-copy-btn");
        btn.textContent = "✅ Copied!";
        btn.classList.add("rg-copied");
        setTimeout(() => {
          btn.innerHTML = "📋 Copy";
          btn.classList.remove("rg-copied");
        }, 2000);
      });
    });

    // Save button
    container.querySelector(".rg-save-btn").addEventListener("click", () => {
      saveReply(text, selectedTone, PLATFORM);
      const btn = container.querySelector(".rg-save-btn");
      btn.textContent = "✅ Saved!";
      btn.classList.add("rg-copied");
      setTimeout(() => {
        btn.innerHTML = "🔖 Save";
        btn.classList.remove("rg-copied");
      }, 2000);
    });

    // Regenerate button (in output area – triggers main generate btn)
    container.querySelector(".rg-regen-btn").addEventListener("click", () => {
      generateBtn.click();
    });
  }
}

// ── Save reply to chrome.storage.local ─────────────────────────────────────
function saveReply(text, tone, platform) {
  const entry = { text, tone, platform, savedAt: Date.now() };
  savedReplies.unshift(entry);
  if (savedReplies.length > 50) savedReplies.pop(); // cap at 50
  chrome.storage.local.set({ savedReplies });
}

// ── Send message to background service worker (promise wrapper) ─────────────
function sendMessage(msg) {
  return new Promise((resolve, reject) => {
    try {
      chrome.runtime.sendMessage(msg, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    } catch (err) {
      reject(err);
    }
  });
}

// ── HTML escape utility ─────────────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

// ── MutationObserver: watch for dynamically loaded posts ───────────────────
// Social platforms are SPAs – posts are added dynamically, so we observe DOM changes.
let debounceTimer;
const observer = new MutationObserver(() => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(injectButtons, 600);
});

observer.observe(document.body, { childList: true, subtree: true });

// Initial injection on page load
injectButtons();
