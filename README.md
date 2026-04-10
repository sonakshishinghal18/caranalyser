# CarIQ India 🚗

**AI-powered car research tool for Indian buyers** — powered by Claude AI (Anthropic)

Upload a car image, snap with your camera, or type a car name. Get instant, comprehensive info: prices, specs, colors, variants, features, pros/cons, competitors & more.

---

## Features

- 📸 **Image Upload** — Upload any car photo to get full details
- 📷 **Camera Capture** — Snap a photo directly from your device
- 🔍 **Text Search** — Type a car name or variant
- 💰 **Indian Pricing** — Ex-showroom prices for all variants
- 🎨 **Color Swatches** — All official colors with visual preview
- ⚡ **Full Specs** — Engine, power, torque, mileage, boot space
- ✦ **Features Breakdown** — Safety, comfort, tech, infotainment
- ⚖ **Pros & Cons** — Honest assessment for Indian buyers
- 🏁 **Competitor Comparison** — Direct rivals with pricing
- 💡 **CarIQ Verdict** — Best variant pick & ideal buyer profile

---

## Tech Stack

- **Backend**: Python + Flask + Anthropic Claude API (claude-opus-4-5)
- **Frontend**: Vanilla HTML/CSS/JS (no frontend framework needed)
- **Hosting**: Render.com (via `render.yaml`)

---

## Local Development

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/cariq-india.git
cd cariq-india
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 5. Run locally
```bash
python app.py
```
Visit `http://localhost:5000`

---

## Deploy on Render

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial CarIQ India commit"
git remote add origin https://github.com/yourusername/cariq-india.git
git push -u origin main
```

### Step 2: Create Render Web Service
1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repository
3. Render will auto-detect `render.yaml`

### Step 3: Set Environment Variable
In Render dashboard → Environment → Add:
```
ANTHROPIC_API_KEY = your_key_here
```

### Step 4: Deploy
Click **Deploy** — your app will be live at `https://cariq-india.onrender.com` (or your custom domain).

---

## Getting an Anthropic API Key

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Go to API Keys → Create Key
3. Copy and set it as `ANTHROPIC_API_KEY` in Render environment variables

---

## Project Structure

```
cariq-india/
├── app.py                  # Flask backend + Claude API integration
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── .env.example            # Environment variable template
├── .gitignore
├── README.md
├── templates/
│   └── index.html          # Main HTML template
└── static/
    ├── css/
    │   └── style.css       # Premium dark automotive UI
    └── js/
        └── app.js          # Frontend logic
```

---

## Notes

- Prices shown are **indicative ex-showroom (Delhi)** — always verify with your local dealer
- Image analysis accuracy depends on image quality and car visibility
- The app uses `claude-opus-4-5` for best accuracy on car identification
- API calls may take 10–20 seconds for complex car analysis
