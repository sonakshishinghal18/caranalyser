import os
import json
import re
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import anthropic

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

CAR_SYSTEM_PROMPT = """You are CarIQ, an expert automotive system for the Indian market.

Always respond in this EXACT JSON format (no markdown, no extra text):
{
  "car_name": "Full car name",
  "brand": "Brand name",
  "model": "Model name",
  "variant_detected": "Variant if identifiable or null",
  "tagline": "A catchy one-liner about this car",
  "year_range": "e.g. 2023-2025",
  "body_type": "Sedan/SUV/Hatchback/MUV/Coupe",
  "fuel_types": ["Petrol"],
  "colors": [
    {"name": "Color Name", "hex": "#hexcode", "type": "solid"}
  ],
  "pricing": {
    "base_variant": "Rs X.XX Lakh",
    "top_variant": "Rs X.XX Lakh",
    "variants": [
      {"name": "Variant Name", "price": "Rs X.XX Lakh", "fuel": "Petrol"}
    ]
  },
  "specifications": {
    "engine": "1.5L 4-cylinder",
    "power": "115 bhp",
    "torque": "144 Nm",
    "transmission": "Manual/Automatic",
    "mileage_arai": "18.6 kmpl",
    "0_to_100": "10.5 seconds",
    "fuel_tank": "50 litres",
    "boot_space": "405 litres"
  },
  "features": {
    "safety": ["Feature 1"],
    "comfort": ["Feature 1"],
    "technology": ["Feature 1"],
    "infotainment": ["Feature 1"]
  },
  "interior": {
    "quality": "Premium",
    "screen_size": "10.25-inch",
    "seating": "5-seater",
    "upholstery": "Leatherette",
    "highlights": ["Highlight 1"]
  },
  "pros": ["Pro 1", "Pro 2"],
  "cons": ["Con 1", "Con 2"],
  "competitors": [
    {"name": "Car Name", "price_range": "Rs X-Y Lakh", "advantage": "reason"}
  ],
  "interesting_facts": ["Fact 1", "Fact 2"],
  "best_variant_pick": "Recommended variant with reason",
  "target_buyer": "Who should buy this",
  "confidence": "high"
}

Rules:
- All prices in Indian Rupees, Lakh format
- Return ONLY valid JSON, nothing else
- For colors give accurate hex codes"""


def analyze_car_image(image_base64, media_type):
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=CAR_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                {"type": "text", "text": "Identify this car and provide complete Indian market information. Return JSON only."}
            ]
        }]
    )
    return parse_response(message.content[0].text)


def analyze_car_text(car_name):
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=CAR_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": "Provide complete Indian market information for: " + car_name + ". Return JSON only."
        }]
    )
    return parse_response(message.content[0].text)


def parse_response(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text.strip())


def get_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CarIQ India</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
:root {
  --bg: #0a0a0b;
  --bg2: #111114;
  --bg3: #18181d;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.12);
  --text: #f0f0f2;
  --text2: #9898a8;
  --text3: #5a5a6e;
  --accent: #e8352e;
  --gold: #c9a84c;
  --green: #2ecc71;
  --red: #e74c3c;
  --card-bg: #13131a;
  --radius: 16px;
  --radius-sm: 10px;
  --fd: 'Bebas Neue', sans-serif;
  --fb: 'DM Sans', sans-serif;
  --fm: 'DM Mono', monospace;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { background: var(--bg); color: var(--text); font-family: var(--fb); min-height: 100vh; overflow-x: hidden; }

.bg-grid { position: fixed; inset: 0; z-index: 0; background-image: linear-gradient(rgba(232,53,46,.03) 1px, transparent 1px), linear-gradient(90deg, rgba(232,53,46,.03) 1px, transparent 1px); background-size: 60px 60px; pointer-events: none; }
.bg-glow { position: fixed; inset: 0; z-index: 0; background: radial-gradient(ellipse 80% 60% at 50% -20%, rgba(232,53,46,.08) 0%, transparent 60%); pointer-events: none; }

.header { position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 0 32px; height: 64px; background: rgba(10,10,11,.9); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); }
.logo { display: flex; align-items: center; gap: 10px; }
.logo-mark { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: var(--accent); color: #fff; font-family: var(--fd); font-size: 18px; border-radius: 8px; }
.logo-text { display: flex; flex-direction: column; line-height: 1; }
.logo-car { font-family: var(--fd); font-size: 20px; letter-spacing: 3px; }
.logo-sub { font-family: var(--fm); font-size: 9px; letter-spacing: 4px; color: var(--accent); text-transform: uppercase; }
.header-tag { font-family: var(--fm); font-size: 11px; color: var(--text3); padding: 4px 10px; border: 1px solid var(--border); border-radius: 20px; }

.hero { position: relative; z-index: 1; text-align: center; padding: 80px 20px 60px; max-width: 860px; margin: 0 auto; }
.hero-eyebrow { font-family: var(--fm); font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--accent); margin-bottom: 20px; display: inline-block; padding: 6px 16px; border: 1px solid rgba(232,53,46,.3); border-radius: 20px; background: rgba(232,53,46,.05); }
.hero-title { font-family: var(--fd); font-size: clamp(56px, 12vw, 110px); line-height: .92; margin-bottom: 24px; }
.title-white { display: block; color: var(--text); }
.title-red { display: block; color: var(--accent); }
.hero-sub { font-size: 16px; color: var(--text2); line-height: 1.7; max-width: 560px; margin: 0 auto 48px; }

.search-card { background: var(--bg3); border: 1px solid var(--border2); border-radius: 20px; overflow: hidden; box-shadow: 0 40px 80px rgba(0,0,0,.4); }
.tab-bar { display: flex; border-bottom: 1px solid var(--border); background: var(--bg2); }
.tab-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 20px; background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; font-family: var(--fb); font-size: 13px; font-weight: 500; color: var(--text3); transition: all .2s; }
.tab-btn:hover { color: var(--text2); }
.tab-btn.active { color: var(--text); border-bottom-color: var(--accent); }
.tab-panel { display: none; padding: 28px; }
.tab-panel.active { display: block; }

.search-row { display: flex; gap: 10px; background: var(--bg2); border: 1px solid var(--border2); border-radius: var(--radius-sm); padding: 6px 6px 6px 18px; transition: border-color .2s; }
.search-row:focus-within { border-color: var(--accent); }
.search-input { flex: 1; background: none; border: none; outline: none; font-family: var(--fb); font-size: 15px; color: var(--text); padding: 10px 0; }
.search-input::placeholder { color: var(--text3); }
.btn-red { display: flex; align-items: center; gap: 8px; padding: 12px 20px; background: var(--accent); border: none; border-radius: 8px; cursor: pointer; font-family: var(--fb); font-size: 14px; font-weight: 600; color: #fff; transition: all .2s; white-space: nowrap; }
.btn-red:hover { background: #c42b25; transform: translateY(-1px); }
.btn-red.wide { width: 100%; justify-content: center; margin-top: 16px; padding: 16px; }

.chips { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
.chip-lbl { font-size: 12px; color: var(--text3); }
.chip { padding: 6px 14px; background: rgba(255,255,255,.04); border: 1px solid var(--border); border-radius: 20px; cursor: pointer; font-family: var(--fb); font-size: 12px; color: var(--text2); transition: all .15s; }
.chip:hover { background: rgba(232,53,46,.1); border-color: rgba(232,53,46,.3); color: var(--text); }

.drop-zone { border: 2px dashed var(--border2); border-radius: var(--radius); padding: 48px 24px; text-align: center; cursor: pointer; transition: all .2s; }
.drop-zone:hover { border-color: var(--accent); background: rgba(232,53,46,.02); }
.drop-icon { color: var(--text3); margin-bottom: 16px; }
.drop-title { font-size: 15px; font-weight: 500; color: var(--text2); margin-bottom: 6px; }
.drop-sub { font-size: 12px; color: var(--text3); }
.preview-wrap { margin-top: 16px; position: relative; display: inline-block; }
.preview-img { max-height: 200px; max-width: 100%; border-radius: 10px; display: block; }
.clear-btn { position: absolute; top: -10px; right: -10px; background: var(--accent); color: #fff; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; font-size: 13px; font-weight: bold; }

.cam-wrap { border-radius: var(--radius); overflow: hidden; background: #000; position: relative; }
.cam-video { width: 100%; max-height: 280px; display: block; object-fit: cover; }
.cam-corners { position: absolute; inset: 0; pointer-events: none; }
.corner { position: absolute; width: 24px; height: 24px; border-color: var(--accent); border-style: solid; opacity: .8; }
.corner.tl { top: 12px; left: 12px; border-width: 2px 0 0 2px; }
.corner.tr { top: 12px; right: 12px; border-width: 2px 2px 0 0; }
.corner.bl { bottom: 12px; left: 12px; border-width: 0 0 2px 2px; }
.corner.br { bottom: 12px; right: 12px; border-width: 0 2px 2px 0; }
.captured-wrap { text-align: center; width: 100%; }
.retake-btn { margin-top: 12px; background: var(--bg2); border: 1px solid var(--border2); color: var(--text2); padding: 8px 16px; border-radius: 8px; cursor: pointer; font-family: var(--fb); font-size: 13px; }
.cam-controls { display: flex; gap: 10px; justify-content: center; margin-top: 16px; flex-wrap: wrap; }
.btn-outline { display: flex; align-items: center; gap: 8px; padding: 12px 20px; background: var(--bg2); border: 1px solid var(--border2); border-radius: var(--radius-sm); cursor: pointer; font-family: var(--fb); font-size: 14px; color: var(--text2); transition: all .2s; }
.btn-outline:hover { border-color: var(--accent); color: var(--text); }
.btn-snap { background: var(--accent); border-color: var(--accent); color: #fff; }

.loading-overlay { position: fixed; inset: 0; z-index: 200; background: rgba(10,10,11,.92); backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: center; }
.loading-inner { text-align: center; }
.spinner { width: 60px; height: 60px; margin: 0 auto 24px; border-radius: 50%; border: 2px solid rgba(255,255,255,.08); border-top-color: var(--accent); animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-title { font-family: var(--fd); font-size: 28px; color: var(--text); }
.loading-sub { font-size: 14px; color: var(--text3); margin-top: 8px; }

.results { position: relative; z-index: 1; padding: 60px 20px 80px; }
.results-inner { max-width: 1100px; margin: 0 auto; }

.car-banner { display: flex; align-items: center; justify-content: space-between; gap: 32px; background: linear-gradient(135deg, #1a0e0d, var(--bg3)); border: 1px solid rgba(232,53,46,.15); border-radius: 24px; padding: 48px; margin-bottom: 28px; position: relative; overflow: hidden; }
.car-banner::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(232,53,46,.5), transparent); }
.banner-content { flex: 1; }
.car-badge { display: inline-block; font-family: var(--fm); font-size: 11px; letter-spacing: 3px; text-transform: uppercase; color: var(--accent); padding: 5px 12px; border: 1px solid rgba(232,53,46,.3); border-radius: 20px; margin-bottom: 16px; }
.car-name { font-family: var(--fd); font-size: clamp(36px, 6vw, 64px); line-height: .95; margin-bottom: 12px; }
.car-tagline { font-size: 15px; color: var(--text2); margin-bottom: 20px; font-style: italic; }
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; }
.meta-chip { font-family: var(--fm); font-size: 12px; padding: 5px 12px; background: rgba(255,255,255,.05); border: 1px solid var(--border); border-radius: 20px; color: var(--text2); }
.meta-chip.gold { background: rgba(201,168,76,.1); border-color: rgba(201,168,76,.3); color: var(--gold); }
.banner-initial { flex-shrink: 0; width: 160px; height: 120px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 16px; font-family: var(--fd); font-size: 40px; color: var(--text3); }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: var(--card-bg); border: 1px solid rgba(255,255,255,.06); border-radius: var(--radius); padding: 28px; animation: up .5s ease both; }
@keyframes up { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.card:nth-child(1){animation-delay:.05s} .card:nth-child(2){animation-delay:.1s} .card:nth-child(3){animation-delay:.15s} .card:nth-child(4){animation-delay:.2s} .card:nth-child(5){animation-delay:.25s} .card:nth-child(6){animation-delay:.3s} .card:nth-child(7){animation-delay:.35s} .card:nth-child(8){animation-delay:.4s}
.card.wide { grid-column: 1 / -1; }
.card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.card-icon { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: rgba(232,53,46,.1); border: 1px solid rgba(232,53,46,.2); border-radius: 8px; font-size: 13px; color: var(--accent); font-family: var(--fm); }
.card-head h3 { font-size: 15px; font-weight: 600; flex: 1; }
.card-note { font-size: 11px; color: var(--text3); font-family: var(--fm); }

.price-box { margin-bottom: 20px; padding: 16px; background: rgba(201,168,76,.05); border: 1px solid rgba(201,168,76,.15); border-radius: var(--radius-sm); text-align: center; }
.price-big { font-family: var(--fd); font-size: 28px; color: var(--gold); }
.price-lbl { font-size: 11px; color: var(--text3); margin-top: 4px; font-family: var(--fm); }
.variants { display: flex; flex-direction: column; gap: 8px; max-height: 280px; overflow-y: auto; }
.variant-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(255,255,255,.03); border: 1px solid var(--border); border-radius: 8px; }
.v-name { font-size: 13px; color: var(--text2); flex: 1; }
.v-fuel { font-family: var(--fm); font-size: 10px; padding: 3px 8px; border-radius: 10px; margin: 0 10px; }
.fuel-petrol { background: rgba(255,107,53,.1); color: #ff6b35; border: 1px solid rgba(255,107,53,.2); }
.fuel-diesel { background: rgba(52,152,219,.1); color: #3498db; border: 1px solid rgba(52,152,219,.2); }
.fuel-electric { background: rgba(46,204,113,.1); color: var(--green); border: 1px solid rgba(46,204,113,.2); }
.fuel-cng { background: rgba(155,89,182,.1); color: #9b59b6; border: 1px solid rgba(155,89,182,.2); }
.v-price { font-family: var(--fm); font-size: 13px; font-weight: 500; }

.specs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.spec-box { padding: 12px; background: rgba(255,255,255,.02); border: 1px solid var(--border); border-radius: 8px; }
.spec-lbl { font-size: 11px; color: var(--text3); font-family: var(--fm); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
.spec-val { font-size: 14px; font-weight: 600; }

.colors-row { display: flex; flex-wrap: wrap; gap: 14px; }
.swatch-wrap { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.swatch { width: 44px; height: 44px; border-radius: 50%; border: 2px solid rgba(255,255,255,.12); box-shadow: 0 4px 12px rgba(0,0,0,.4), inset 0 1px 1px rgba(255,255,255,.15); transition: transform .2s; }
.swatch:hover { transform: scale(1.12); }
.swatch-name { font-size: 10px; color: var(--text3); text-align: center; max-width: 60px; line-height: 1.3; }

.feat-tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.feat-tab { padding: 5px 12px; border-radius: 20px; cursor: pointer; font-size: 12px; font-weight: 500; background: rgba(255,255,255,.04); border: 1px solid var(--border); color: var(--text3); transition: all .15s; }
.feat-tab.active { background: rgba(232,53,46,.1); border-color: rgba(232,53,46,.3); color: var(--text); }
.feat-list { display: flex; flex-direction: column; gap: 8px; }
.feat-item { display: flex; align-items: flex-start; gap: 10px; font-size: 13px; color: var(--text2); line-height: 1.4; }
.feat-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex-shrink: 0; margin-top: 5px; }

.int-rows { display: flex; flex-direction: column; }
.int-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); }
.int-row:last-child { border-bottom: none; }
.int-lbl { font-size: 12px; color: var(--text3); font-family: var(--fm); }
.int-val { font-size: 13px; font-weight: 500; }
.q-badge { padding: 3px 10px; border-radius: 10px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.q-premium { background: rgba(201,168,76,.1); color: var(--gold); border: 1px solid rgba(201,168,76,.2); }
.q-good { background: rgba(46,204,113,.1); color: var(--green); border: 1px solid rgba(46,204,113,.2); }
.q-average { background: rgba(52,152,219,.1); color: #3498db; border: 1px solid rgba(52,152,219,.2); }
.q-budget { background: rgba(255,255,255,.05); color: var(--text3); border: 1px solid var(--border); }

.pc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.pc-head { font-size: 11px; font-family: var(--fm); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
.pc-head.green { color: var(--green); }
.pc-head.red { color: var(--red); }
.pc-item { display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: var(--text2); line-height: 1.4; margin-bottom: 8px; }
.pc-icon { flex-shrink: 0; font-weight: bold; }
.pc-icon.green { color: var(--green); }
.pc-icon.red { color: var(--red); }

.comp-list { display: flex; flex-direction: column; gap: 12px; }
.comp-card { padding: 14px; background: rgba(255,255,255,.02); border: 1px solid var(--border); border-radius: 10px; }
.comp-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.comp-name { font-size: 14px; font-weight: 600; }
.comp-price { font-family: var(--fm); font-size: 12px; color: var(--gold); }
.comp-why { font-size: 12px; color: var(--text3); line-height: 1.4; }

.verdict-pick { background: linear-gradient(135deg, rgba(232,53,46,.08), rgba(232,53,46,.03)); border: 1px solid rgba(232,53,46,.15); border-radius: var(--radius-sm); padding: 16px; margin-bottom: 16px; }
.verdict-lbl { font-size: 11px; color: var(--accent); font-family: var(--fm); letter-spacing: 2px; margin-bottom: 8px; }
.verdict-txt { font-size: 14px; line-height: 1.5; }
.target-box { display: flex; align-items: center; gap: 10px; padding: 12px; background: rgba(255,255,255,.02); border-radius: 8px; margin-bottom: 16px; }
.target-lbl { font-size: 11px; color: var(--text3); font-family: var(--fm); white-space: nowrap; }
.target-txt { font-size: 13px; color: var(--text2); }
.facts { display: flex; flex-direction: column; gap: 8px; }
.fact { display: flex; gap: 10px; align-items: flex-start; font-size: 13px; color: var(--text2); line-height: 1.4; }
.fact-n { font-family: var(--fm); font-size: 11px; color: var(--accent); width: 20px; flex-shrink: 0; }

.reset-wrap { text-align: center; margin-top: 48px; }
.reset-btn { display: inline-flex; align-items: center; gap: 10px; padding: 14px 28px; background: transparent; border: 1px solid var(--border2); border-radius: 30px; cursor: pointer; font-family: var(--fb); font-size: 14px; color: var(--text2); transition: all .2s; }
.reset-btn:hover { border-color: var(--accent); color: var(--text); }

footer { position: relative; z-index: 1; text-align: center; padding: 24px; border-top: 1px solid var(--border); font-size: 12px; color: var(--text3); font-family: var(--fm); }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

@media (max-width: 600px) {
  .header { padding: 0 16px; }
  .hero { padding: 48px 16px 40px; }
  .tab-panel { padding: 20px; }
  .car-banner { flex-direction: column; padding: 28px 20px; }
  .banner-initial { display: none; }
  .grid { grid-template-columns: 1fr; }
  .card.wide { grid-column: 1; }
  .pc-grid { grid-template-columns: 1fr; }
  .specs-grid { grid-template-columns: 1fr 1fr; }
}
</style>
</head>
<body>

<div class="bg-grid"></div>
<div class="bg-glow"></div>

<header class="header">
  <div class="logo">
    <span class="logo-mark">IQ</span>
    <div class="logo-text">
      <span class="logo-car">CAR</span>
      <span class="logo-sub">INDIA</span>
    </div>
  </div>
  <span class="header-tag">Smart Car Research</span>
</header>

<section class="hero" id="heroSection">
  <div class="hero-eyebrow">India's Smartest Car Research Tool</div>
  <h1 class="hero-title">
    <span class="title-white">EVERY CAR.</span>
    <span class="title-red">EVERY DETAIL.</span>
  </h1>
  <p class="hero-sub">Upload a photo, snap with camera, or type a car name. Get instant insights — prices, specs, colors, features &amp; more.</p>

  <div class="search-card">
    <div class="tab-bar">
      <button class="tab-btn active" id="tabText" onclick="switchTab('text')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        Search by Name
      </button>
      <button class="tab-btn" id="tabUpload" onclick="switchTab('upload')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        Upload Image
      </button>
      <button class="tab-btn" id="tabCamera" onclick="switchTab('camera')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
        Camera
      </button>
    </div>

    <div class="tab-panel active" id="panelText">
      <div class="search-row">
        <input type="text" class="search-input" id="carInput" placeholder="e.g. Tata Nexon EV, Maruti Swift ZXi+, Hyundai Creta..." autocomplete="off"/>
        <button class="btn-red" id="analyseTextBtn">
          Analyse
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>
      <div class="chips">
        <span class="chip-lbl">Popular:</span>
        <button class="chip" onclick="doQuickSearch('Tata Nexon EV')">Nexon EV</button>
        <button class="chip" onclick="doQuickSearch('Maruti Suzuki Swift 2024')">Swift 2024</button>
        <button class="chip" onclick="doQuickSearch('Hyundai Creta 2024')">Creta 2024</button>
        <button class="chip" onclick="doQuickSearch('Mahindra XEV 9e')">XEV 9e</button>
        <button class="chip" onclick="doQuickSearch('Kia Syros')">Kia Syros</button>
      </div>
    </div>

    <div class="tab-panel" id="panelUpload">
      <div class="drop-zone" id="dropZone">
        <div class="drop-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        </div>
        <p class="drop-title">Drop car image here</p>
        <p class="drop-sub">or click to browse — JPG, PNG, WEBP</p>
        <div class="preview-wrap" id="previewWrap" style="display:none">
          <img id="previewImg" class="preview-img" alt=""/>
          <button class="clear-btn" id="clearImgBtn">&#x2715;</button>
        </div>
      </div>
      <input type="file" id="fileInput" accept="image/*" style="display:none"/>
      <button class="btn-red wide" id="analyseImgBtn" style="display:none">
        Analyse This Car
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg>
      </button>
    </div>

    <div class="tab-panel" id="panelCamera">
      <div class="cam-wrap" id="camWrap">
        <video id="camVideo" class="cam-video" autoplay playsinline></video>
        <canvas id="camCanvas" style="display:none"></canvas>
        <div class="cam-corners">
          <div class="corner tl"></div><div class="corner tr"></div>
          <div class="corner bl"></div><div class="corner br"></div>
        </div>
      </div>
      <div class="captured-wrap" id="capturedWrap" style="display:none">
        <img id="capturedImg" class="preview-img" alt=""/>
        <br/>
        <button class="retake-btn" id="retakeBtn">&#8635; Retake</button>
      </div>
      <div class="cam-controls">
        <button class="btn-outline" id="startCamBtn">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
          Start Camera
        </button>
        <button class="btn-outline btn-snap" id="snapBtn" style="display:none">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>
          Capture
        </button>
        <button class="btn-red" id="analyseCamBtn" style="display:none">
          Analyse
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>
    </div>
  </div>
</section>

<div class="loading-overlay" id="loadingOverlay" style="display:none">
  <div class="loading-inner">
    <div class="spinner"></div>
    <div class="loading-title" id="loadingMsg">Identifying your car...</div>
    <div class="loading-sub">Fetching specs, prices &amp; features</div>
  </div>
</div>

<section class="results" id="resultsSection" style="display:none">
  <div class="results-inner">

    <div class="car-banner">
      <div class="banner-content">
        <div class="car-badge" id="rBadge"></div>
        <div class="car-name" id="rName"></div>
        <div class="car-tagline" id="rTagline"></div>
        <div class="meta-row">
          <span class="meta-chip" id="rBodyType"></span>
          <span class="meta-chip" id="rYear"></span>
          <span class="meta-chip gold" id="rPrice"></span>
        </div>
      </div>
      <div class="banner-initial" id="rInitial"></div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-head"><div class="card-icon">Rs</div><h3>Pricing</h3><span class="card-note">Ex-showroom, Delhi</span></div>
        <div class="price-box" id="rPriceBox"></div>
        <div class="variants" id="rVariants"></div>
      </div>

      <div class="card">
        <div class="card-head"><div class="card-icon">--</div><h3>Specifications</h3></div>
        <div class="specs-grid" id="rSpecs"></div>
      </div>

      <div class="card">
        <div class="card-head"><div class="card-icon">[]</div><h3>Colors</h3></div>
        <div class="colors-row" id="rColors"></div>
      </div>

      <div class="card wide">
        <div class="card-head"><div class="card-icon">*</div><h3>Features</h3></div>
        <div class="feat-tabs" id="rFeatTabs"></div>
        <div class="feat-list" id="rFeatList"></div>
      </div>

      <div class="card">
        <div class="card-head"><div class="card-icon">~</div><h3>Interior</h3></div>
        <div class="int-rows" id="rInterior"></div>
      </div>

      <div class="card">
        <div class="card-head"><div class="card-icon">+-</div><h3>Pros &amp; Cons</h3></div>
        <div class="pc-grid" id="rProscons"></div>
      </div>

      <div class="card">
        <div class="card-head"><div class="card-icon">vs</div><h3>Competition</h3></div>
        <div class="comp-list" id="rComps"></div>
      </div>

      <div class="card wide">
        <div class="card-head"><div class="card-icon">!</div><h3>Verdict</h3></div>
        <div id="rVerdict"></div>
        <div class="facts" id="rFacts"></div>
      </div>
    </div>

    <div class="reset-wrap">
      <button class="reset-btn" id="resetBtn">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.87"/></svg>
        Search Another Car
      </button>
    </div>
  </div>
</section>

<footer>CarIQ India &mdash; Smart car research for Indian buyers &mdash; Prices are indicative, verify with dealer</footer>

<script>
(function() {
  // State
  var uploadedImg = null;
  var capturedImg = null;
  var camStream = null;
  var featData = {};
  var loadTimer = null;

  var loadMsgs = [
    'Identifying your car...',
    'Scanning Indian market prices...',
    'Fetching variants and colors...',
    'Pulling specs and features...',
    'Preparing your report...'
  ];

  // ── Helpers ──────────────────────────────────────────────────────────────
  function esc(s) {
    return String(s || '')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;');
  }

  function el(id) { return document.getElementById(id); }

  function showLoad() {
    el('loadingOverlay').style.display = 'flex';
    var i = 0;
    el('loadingMsg').textContent = loadMsgs[0];
    loadTimer = setInterval(function() {
      i = (i + 1) % loadMsgs.length;
      el('loadingMsg').textContent = loadMsgs[i];
    }, 1800);
  }

  function hideLoad() {
    clearInterval(loadTimer);
    el('loadingOverlay').style.display = 'none';
  }

  // ── Tabs ─────────────────────────────────────────────────────────────────
  window.switchTab = function(tab) {
    var tabs = ['text','upload','camera'];
    tabs.forEach(function(t) {
      el('tab' + t.charAt(0).toUpperCase() + t.slice(1)).classList.remove('active');
      el('panel' + t.charAt(0).toUpperCase() + t.slice(1)).classList.remove('active');
    });
    el('tab' + tab.charAt(0).toUpperCase() + tab.slice(1)).classList.add('active');
    el('panel' + tab.charAt(0).toUpperCase() + tab.slice(1)).classList.add('active');
    if (tab !== 'camera' && camStream) stopCam();
  };

  // ── Text search ───────────────────────────────────────────────────────────
  window.doQuickSearch = function(q) {
    el('carInput').value = q;
    doTextSearch();
  };

  function doTextSearch() {
    var q = el('carInput').value.trim();
    if (!q) return;
    callAPI('/api/analyze/text', { query: q });
  }

  // ── Upload ────────────────────────────────────────────────────────────────
  el('dropZone').addEventListener('click', function() {
    el('fileInput').click();
  });

  el('dropZone').addEventListener('dragover', function(e) { e.preventDefault(); });

  el('dropZone').addEventListener('drop', function(e) {
    e.preventDefault();
    var f = e.dataTransfer.files[0];
    if (f && f.type.startsWith('image/')) loadFile(f);
  });

  el('fileInput').addEventListener('change', function(e) {
    var f = e.target.files[0];
    if (f) loadFile(f);
  });

  function loadFile(f) {
    var reader = new FileReader();
    reader.onload = function(ev) {
      uploadedImg = ev.target.result;
      el('previewImg').src = uploadedImg;
      el('previewWrap').style.display = 'block';
      el('dropZone').querySelector('.drop-icon').style.display = 'none';
      el('dropZone').querySelector('.drop-title').style.display = 'none';
      el('dropZone').querySelector('.drop-sub').style.display = 'none';
      el('analyseImgBtn').style.display = 'flex';
    };
    reader.readAsDataURL(f);
  }

  el('clearImgBtn').addEventListener('click', function(e) {
    e.stopPropagation();
    uploadedImg = null;
    el('previewWrap').style.display = 'none';
    el('dropZone').querySelector('.drop-icon').style.display = 'block';
    el('dropZone').querySelector('.drop-title').style.display = 'block';
    el('dropZone').querySelector('.drop-sub').style.display = 'block';
    el('analyseImgBtn').style.display = 'none';
    el('fileInput').value = '';
  });

  el('analyseImgBtn').addEventListener('click', function() {
    if (uploadedImg) callAPI('/api/analyze/image', { image: uploadedImg });
  });

  // ── Camera ────────────────────────────────────────────────────────────────
  el('startCamBtn').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      .then(function(stream) {
        camStream = stream;
        el('camVideo').srcObject = stream;
        el('startCamBtn').style.display = 'none';
        el('snapBtn').style.display = 'flex';
      })
      .catch(function() {
        alert('Camera access denied. Please use file upload instead.');
      });
  });

  el('snapBtn').addEventListener('click', function() {
    var v = el('camVideo');
    var c = el('camCanvas');
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    capturedImg = c.toDataURL('image/jpeg', 0.92);
    el('capturedImg').src = capturedImg;
    el('camWrap').style.display = 'none';
    el('capturedWrap').style.display = 'block';
    el('snapBtn').style.display = 'none';
    el('analyseCamBtn').style.display = 'flex';
    stopCam();
  });

  el('retakeBtn').addEventListener('click', function() {
    capturedImg = null;
    el('capturedWrap').style.display = 'none';
    el('analyseCamBtn').style.display = 'none';
    el('camWrap').style.display = 'block';
    el('startCamBtn').style.display = 'flex';
    el('startCamBtn').click();
  });

  el('analyseCamBtn').addEventListener('click', function() {
    if (capturedImg) callAPI('/api/analyze/image', { image: capturedImg });
  });

  function stopCam() {
    if (camStream) {
      camStream.getTracks().forEach(function(t) { t.stop(); });
      camStream = null;
    }
  }

  // ── Analyse text button ───────────────────────────────────────────────────
  el('analyseTextBtn').addEventListener('click', doTextSearch);
  el('carInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') doTextSearch();
  });

  // ── Reset ─────────────────────────────────────────────────────────────────
  el('resetBtn').addEventListener('click', function() {
    el('heroSection').style.display = 'block';
    el('resultsSection').style.display = 'none';
    el('carInput').value = '';
    uploadedImg = null;
    capturedImg = null;
    switchTab('text');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // ── API call ──────────────────────────────────────────────────────────────
  function callAPI(url, payload) {
    showLoad();
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function(res) { return res.json(); })
    .then(function(r) {
      hideLoad();
      if (!r.success) throw new Error(r.error || 'Analysis failed');
      renderResults(r.data);
    })
    .catch(function(err) {
      hideLoad();
      alert('Error: ' + err.message);
    });
  }

  // ── Render ────────────────────────────────────────────────────────────────
  function renderResults(d) {
    el('heroSection').style.display = 'none';
    el('resultsSection').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Banner
    el('rBadge').textContent = (d.brand || '') + (d.body_type ? ' — ' + d.body_type : '');
    el('rName').textContent = d.car_name || d.model || 'Unknown Car';
    el('rTagline').textContent = d.tagline || '';
    el('rBodyType').textContent = d.body_type || '';
    el('rYear').textContent = d.year_range || '';
    var p = d.pricing || {};
    el('rPrice').textContent = (p.base_variant && p.top_variant)
      ? p.base_variant + ' – ' + p.top_variant
      : p.base_variant || p.top_variant || '';
    var nm = d.car_name || d.model || '?';
    el('rInitial').textContent = nm.split(' ').slice(0,2).map(function(w){return w[0];}).join('').toUpperCase();

    // Pricing
    el('rPriceBox').innerHTML = (p.base_variant || p.top_variant)
      ? '<div class="price-big">' + esc(p.base_variant||'') + (p.base_variant && p.top_variant ? ' – ' : '') + esc(p.top_variant||'') + '</div><div class="price-lbl">Ex-showroom · Delhi</div>'
      : '';
    el('rVariants').innerHTML = (p.variants || []).map(function(v) {
      return '<div class="variant-row"><span class="v-name">' + esc(v.name) + '</span>'
        + '<span class="v-fuel fuel-' + (v.fuel||'').toLowerCase() + '">' + esc(v.fuel) + '</span>'
        + '<span class="v-price">' + esc(v.price) + '</span></div>';
    }).join('');

    // Specs
    var sm = [['Engine','engine'],['Power','power'],['Torque','torque'],['Transmission','transmission'],
              ['Mileage','mileage_arai'],['0-100','0_to_100'],['Fuel Tank','fuel_tank'],['Boot','boot_space']];
    var s = d.specifications || {};
    el('rSpecs').innerHTML = sm.filter(function(i){return s[i[1]];}).map(function(i){
      return '<div class="spec-box"><div class="spec-lbl">' + i[0] + '</div><div class="spec-val">' + esc(s[i[1]]) + '</div></div>';
    }).join('');

    // Colors
    el('rColors').innerHTML = (d.colors || []).map(function(c) {
      return '<div class="swatch-wrap">'
        + '<div class="swatch" style="background:' + esc(c.hex||'#888') + '" title="' + esc(c.name) + '"></div>'
        + '<span class="swatch-name">' + esc(c.name) + '</span></div>';
    }).join('');

    // Features
    featData = d.features || {};
    var cats = ['safety','comfort','technology','infotainment'];
    el('rFeatTabs').innerHTML = cats.filter(function(c){return featData[c]&&featData[c].length;})
      .map(function(c,i) {
        return '<button class="feat-tab' + (i===0?' active':'') + '" onclick="showFeat(\'' + c + '\',this)">'
          + c.charAt(0).toUpperCase() + c.slice(1) + '</button>';
      }).join('');
    var firstCat = cats.find(function(c){return featData[c]&&featData[c].length;});
    if (firstCat) showFeat(firstCat, null);

    // Interior
    var it = d.interior || {};
    var qc = (it.quality || 'average').toLowerCase();
    el('rInterior').innerHTML = [
      ['QUALITY', '<span class="q-badge q-' + qc + '">' + esc(it.quality||'N/A') + '</span>'],
      ['SEATING', esc(it.seating||'N/A')],
      ['SCREEN', esc(it.screen_size||'N/A')],
      ['UPHOLSTERY', esc(it.upholstery||'N/A')]
    ].map(function(x){
      return '<div class="int-row"><span class="int-lbl">' + x[0] + '</span><span class="int-val">' + x[1] + '</span></div>';
    }).join('') + ((it.highlights&&it.highlights.length)
      ? it.highlights.map(function(h){return '<div class="feat-item"><div class="feat-dot"></div><span>'+esc(h)+'</span></div>';}).join('')
      : '');

    // Pros/Cons
    el('rProscons').innerHTML =
      '<div><div class="pc-head green">PROS</div>' + (d.pros||[]).map(function(x){
        return '<div class="pc-item"><span class="pc-icon green">+</span><span>'+esc(x)+'</span></div>';
      }).join('') + '</div>'
      + '<div><div class="pc-head red">CONS</div>' + (d.cons||[]).map(function(x){
        return '<div class="pc-item"><span class="pc-icon red">-</span><span>'+esc(x)+'</span></div>';
      }).join('') + '</div>';

    // Competitors
    el('rComps').innerHTML = (d.competitors||[]).map(function(c){
      return '<div class="comp-card"><div class="comp-top"><span class="comp-name">'+esc(c.name)+'</span>'
        +'<span class="comp-price">'+esc(c.price_range)+'</span></div>'
        +'<div class="comp-why">'+esc(c.advantage)+'</div></div>';
    }).join('');

    // Verdict
    el('rVerdict').innerHTML =
      (d.best_variant_pick ? '<div class="verdict-pick"><div class="verdict-lbl">BEST PICK</div><div class="verdict-txt">'+esc(d.best_variant_pick)+'</div></div>' : '')
      + (d.target_buyer ? '<div class="target-box"><span class="target-lbl">IDEAL FOR</span><span class="target-txt">'+esc(d.target_buyer)+'</span></div>' : '');

    el('rFacts').innerHTML = (d.interesting_facts||[]).map(function(f,i){
      return '<div class="fact"><span class="fact-n">0'+(i+1)+'</span><span>'+esc(f)+'</span></div>';
    }).join('');
  }

  // ── Feature tabs ──────────────────────────────────────────────────────────
  window.showFeat = function(cat, btn) {
    if (btn) {
      document.querySelectorAll('.feat-tab').forEach(function(t){t.classList.remove('active');});
      btn.classList.add('active');
    }
    var items = (featData && featData[cat]) || [];
    el('rFeatList').innerHTML = items.map(function(f){
      return '<div class="feat-item"><div class="feat-dot"></div><span>'+esc(f)+'</span></div>';
    }).join('');
  };

})();
</script>

</body>
</html>"""


@app.route("/")
def index():
    return Response(get_html(), mimetype="text/html")


@app.route("/api/analyze/image", methods=["POST"])
def analyze_image():
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image provided"}), 400
        img = data["image"]
        if "," in img:
            header, b64 = img.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
        else:
            b64 = img
            mime = "image/jpeg"
        result = analyze_car_image(b64, mime)
        return jsonify({"success": True, "data": result})
    except json.JSONDecodeError as e:
        return jsonify({"error": "Could not parse car data", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze/text", methods=["POST"])
def analyze_text():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "No query provided"}), 400
        result = analyze_car_text(data["query"])
        return jsonify({"success": True, "data": result})
    except json.JSONDecodeError as e:
        return jsonify({"error": "Could not parse car data", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
