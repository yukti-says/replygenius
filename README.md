# ✦ ReplyGenius – AI Reply Assistant for Social Media

> Generate human-sounding, intelligent replies for LinkedIn, X (Twitter), Reddit, and Medium — powered by free AI APIs.

---

## 🗂 Project Structure

```
replygenius/
├── extension/                  ← Chrome Extension (Manifest V3)
│   ├── manifest.json           ← Extension config & permissions
│   ├── icons/                  ← 16, 48, 128px icons
│   ├── background/
│   │   └── service_worker.js   ← Background script (handles API calls)
│   ├── content/
│   │   ├── content.js          ← Injected into social media pages
│   │   └── content.css         ← Styles for injected UI
│   └── popup/
│       ├── popup.html          ← Extension popup UI
│       ├── popup.css           ← Popup styles
│       └── popup.js            ← Popup logic (tabs, settings, saved)
│
└── backend/                    ← Flask Python Backend
    ├── app.py                  ← Flask app entry point
    ├── requirements.txt        ← Python dependencies
    ├── .env.example            ← API key template
    ├── Procfile                ← For Render/Railway deployment
    ├── render.yaml             ← One-click Render config
    ├── routes/
    │   ├── __init__.py
    │   ├── generate.py         ← POST /api/generate
    │   └── health.py           ← GET /api/health
    └── utils/
        ├── __init__.py
        ├── ai_client.py        ← Gemini / Groq / OpenRouter clients
        └── prompt_builder.py   ← Smart prompt construction per tone/platform
```

---

## ⚡ Quick Start

### Step 1 – Get a Free API Key (pick ONE or more)

#### Option A: Google Gemini (Recommended)
1. Go to → https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click **"Create API Key"**
4. Copy the key (starts with `AIza...`)

#### Option B: Groq (Fastest)
1. Go to → https://console.groq.com/keys
2. Sign up (free, no credit card)
3. Click **"Create API Key"**
4. Copy the key (starts with `gsk_...`)

#### Option C: OpenRouter (Most models)
1. Go to → https://openrouter.ai/keys
2. Sign up (free)
3. Click **"Create Key"**
4. Copy the key (starts with `sk-or-...`)

---

### Step 2 – Set Up the Backend

```bash
# 1. Navigate to backend folder
cd replygenius/backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your .env file
cp .env.example .env

# 6. Open .env and paste your API key(s)
# Example:
# GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX
nano .env      # or use any text editor

# 7. Run the Flask server
python app.py
```

You should see:
```
🚀 ReplyGenius backend running on http://localhost:5000
```

Test it works:
```bash
curl http://localhost:5000/api/health
# → {"service":"ReplyGenius","status":"ok"}
```

---

### Step 3 – Load the Chrome Extension

1. Open Chrome and go to: `chrome://extensions/`
2. Enable **"Developer mode"** (top-right toggle)
3. Click **"Load unpacked"**
4. Select the `replygenius/extension/` folder
5. The **ReplyGenius** icon appears in your toolbar ✦

---

### Step 4 – Use It!

1. Make sure your Flask backend is running (`python app.py`)
2. Open LinkedIn, X (twitter.com or x.com), Reddit, or Medium
3. Scroll to any post with text
4. Look for the **✨ Generate Reply** button under the post
5. Click it → pick a tone → click **✨ Generate Reply**
6. Copy, save, or regenerate as needed

---

## 🎭 Available Tones

| Tone | Best For |
|------|----------|
| 💼 Professional | LinkedIn, formal discussions |
| 🧠 Smart | Intellectual posts, thought leadership |
| 💭 Thoughtful | Long-form content, nuanced topics |
| 😂 Funny | Casual posts, memes, lighthearted content |
| 🔥 Gen Z | Trendy content, youth culture |
| 😊 Casual | Everyday posts, friendly conversations |
| ⚡ Viral | X/Twitter, hot takes, shareable content |
| 🌊 Deep | Philosophy, psychology, existential topics |

---

## 🏗 How It Works (Architecture)

```
Browser (LinkedIn/X/Reddit/Medium)
           │
           │  content.js injected by Chrome
           │  → detects posts via CSS selectors
           │  → injects ✨ Generate Reply button
           │
           ▼
   Background Service Worker
   (background/service_worker.js)
           │
           │  Receives message from content script
           │  Forwards to Flask backend
           │
           ▼
   Flask Backend (app.py)
           │
           │  /api/generate endpoint
           │  Builds smart prompt via prompt_builder.py
           │  Calls AI API via ai_client.py
           │
           ▼
   Free AI API (Gemini / Groq / OpenRouter)
           │
           │  Returns generated reply
           │
           ▼
   Content Script renders reply in panel
   User copies → pastes into comment box
```

### Why a Backend?
- **Security**: API keys stay on the server, never in extension files
- **Flexibility**: Swap AI providers without updating the extension
- **Control**: Add rate limiting, logging, caching server-side

---

## 🚀 Deployment (Free on Render)

### Deploy to Render.com (Free)

1. Push your `backend/` folder to a GitHub repo
2. Go to → https://render.com → "New Web Service"
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2`
   - **Root Directory**: `backend`
5. Add Environment Variables in Render dashboard:
   - `GEMINI_API_KEY` = your key
   - `FLASK_ENV` = `production`
6. Deploy → get your URL like `https://replygenius-xxxx.onrender.com`

### Connect extension to deployed backend

1. Click ReplyGenius extension icon
2. Go to **Settings** tab
3. Change **Backend URL** to your Render URL
4. Click **Save Settings**
5. Click **Test Connection** → should show ✅

### Deploy to Railway.app (Alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# In backend/ directory
cd backend
railway init
railway up
```

---

## 🔧 Troubleshooting

### "✨ Generate Reply" button doesn't appear
- Make sure the extension is loaded in `chrome://extensions/`
- Hard refresh the page (Ctrl+Shift+R)
- LinkedIn/X load dynamically — wait a second after the feed loads
- Check for JS errors: Right-click page → Inspect → Console

### "Backend offline" in popup
- Make sure `python app.py` is running in terminal
- Check the terminal for error messages
- Try visiting `http://localhost:5000/api/health` in browser

### "All AI providers failed" error
- Check your `.env` file has a valid API key
- Make sure there's no extra space around the `=` sign
- Verify the key works by testing it in the AI provider's console
- Check you haven't exceeded free tier limits (Gemini: 60 req/min)

### Extension can't reach localhost after deployment
- In popup Settings, update Backend URL to your Render/Railway URL
- Make sure your deployed backend has CORS enabled (it does by default)

### CORS errors in console
- This is expected in development if extension URL changes
- The backend uses `flask-cors` with `origins: "*"` for extension compatibility

---

## 🛠 Development Tips

### Adding a new platform
1. Open `extension/content/content.js`
2. Add platform to `detectPlatform()` function
3. Add CSS selectors to `SELECTORS` object
4. Add to `manifest.json` → `host_permissions` and `content_scripts.matches`

### Adding a new tone
1. Open `backend/utils/prompt_builder.py`
2. Add an entry to `TONE_INSTRUCTIONS`
3. Open `extension/content/content.js` and add to `TONES` array
4. Open `extension/popup/popup.js` and add to `TONES` array

### Switching AI model
1. Open `backend/utils/ai_client.py`
2. Change the `GROQ_MODEL` or `GEMINI_MODEL` variable at the top
3. For Groq free models: `mixtral-8x7b-32768`, `gemma-7b-it`, `llama3-70b-8192`

---

## 📦 Tech Stack

| Component | Tech |
|-----------|------|
| Extension | Chrome Manifest V3, Vanilla JS, CSS |
| Backend | Python 3.11+, Flask 3, Flask-CORS |
| AI (primary) | Google Gemini 1.5 Flash (free) |
| AI (fallback) | Groq Llama 3 (free) |
| AI (fallback) | OpenRouter free models |
| Deployment | Render / Railway (both free tiers) |

---

## 🔒 Security Notes

- API keys are **only stored in `.env` on the server**
- The extension never sees or stores API keys
- All AI calls go through your backend
- Add rate limiting in production (see Flask-Limiter)

---


