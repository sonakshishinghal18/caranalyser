import os
import json
import re
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import anthropic

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

CAR_SYSTEM_PROMPT = """You are CarIQ — an expert automotive intelligence system specializing exclusively in cars sold in the Indian market. Your role is to provide comprehensive, accurate, and engaging car information to Indian car buyers.

When given a car name, image, or partial information, extract and provide:

1. **Car Identity**: Full name, brand, model, variant (if detectable)
2. **Available Colors**: All official color options with their marketing names
3. **Pricing**: Ex-showroom prices for all variants (mention city as Delhi for reference), on-road price estimate
4. **Key Specifications**: Engine, transmission, fuel type, mileage (ARAI), power, torque, dimensions
5. **Features**: Top features, safety tech, infotainment, comfort, ADAS if available
6. **Interior Details**: Describe interior quality, materials, seating, infotainment screen size
7. **Pros & Cons**: Honest assessment for Indian buyers
8. **Competitors**: 2-3 direct rivals in India with price comparison
9. **Interesting Facts**: Launch date, awards, record sales, unique selling points
10. **Buying Advice**: Best variant for value, fuel type recommendation

Always respond in this EXACT JSON format:
{
  "car_name": "Full car name",
  "brand": "Brand name",
  "model": "Model name",
  "variant_detected": "Variant if identifiable, else null",
  "tagline": "A catchy one-liner about this car",
  "year_range": "e.g. 2023-2025",
  "body_type": "Sedan/SUV/Hatchback/etc",
  "fuel_types": ["Petrol", "Diesel", "CNG", "Electric"],
  "colors": [
    {"name": "Color Marketing Name", "hex": "#hexcode", "type": "solid/metallic/pearl"}
  ],
  "pricing": {
    "base_variant": "Rs X.XX Lakh",
    "top_variant": "Rs X.XX Lakh",
    "variants": [
      {"name": "Variant Name", "price": "Rs X.XX Lakh", "fuel": "Petrol/Diesel/CNG/Electric"}
    ]
  },
  "specifications": {
    "engine": "e.g. 1.5L 4-cylinder",
    "power": "e.g. 115 bhp",
    "torque": "e.g. 144 Nm",
    "transmission": "Manual/Automatic/CVT/DCT",
    "mileage_arai": "e.g. 18.6 kmpl",
    "0_to_100": "e.g. 10.5 seconds (if known)",
    "fuel_tank": "e.g. 50 litres",
    "boot_space": "e.g. 405 litres"
  },
  "features": {
    "safety": ["Feature 1", "Feature 2"],
    "comfort": ["Feature 1", "Feature 2"],
    "technology": ["Feature 1", "Feature 2"],
    "infotainment": ["Feature 1", "Feature 2"]
  },
  "interior": {
    "quality": "Premium/Good/Average/Budget",
    "screen_size": "e.g. 10.25-inch",
    "seating": "e.g. 5-seater",
    "upholstery": "e.g. Leatherette/Fabric/Leather",
    "highlights": ["Interior highlight 1", "Interior highlight 2"]
  },
  "pros": ["Pro 1", "Pro 2", "Pro 3"],
  "cons": ["Con 1", "Con 2"],
  "competitors": [
    {"name": "Car Name", "price_range": "Rs X-Y Lakh", "advantage": "Why someone might pick this instead"}
  ],
  "interesting_facts": ["Fact 1", "Fact 2", "Fact 3"],
  "best_variant_pick": "Recommended variant with reason",
  "target_buyer": "Who should buy this car",
  "image_search_query": "A precise Google Images search query to find good photos of this car in India",
  "confidence": "high/medium/low"
}

IMPORTANT:
- All prices must be in Indian Rupees and in Lakh format
- Be accurate with Indian market pricing
- If you cannot identify the car from an image, set confidence to "low" and provide best guess
- Always return valid JSON only, no markdown, no extra text
- For colors, provide approximate hex codes that match the actual car color"""


def analyze_car_image(image_base64: str, media_type: str) -> dict:
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=CAR_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                {"type": "text", "text": "Identify this car and provide complete information for an Indian buyer. Return JSON only."}
            ],
        }],
    )
    return parse_car_response(message.content[0].text)


def analyze_car_text(car_name: str) -> dict:
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=CAR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Provide complete information for: {car_name}. Return JSON only."}],
    )
    return parse_car_response(message.content[0].text)


def parse_car_response(text: str) -> dict:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text.strip())


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>CarIQ India - Know Every Car</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
  <style>
:root{--bg:#0a0a0b;--bg2:#111114;--bg3:#18181d;--border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.12);--text:#f0f0f2;--text2:#9898a8;--text3:#5a5a6e;--accent:#e8352e;--gold:#c9a84c;--green:#2ecc71;--red:#e74c3c;--card-bg:#13131a;--card-border:rgba(255,255,255,0.06);--radius:16px;--radius-sm:10px;--font-display:'Bebas Neue',sans-serif;--font-body:'DM Sans',sans-serif;--font-mono:'DM Mono',monospace}
*{margin:0;padding:0;box-sizing:border-box}html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--font-body);min-height:100vh;overflow-x:hidden}
.bg-grid{position:fixed;inset:0;z-index:0;background-image:linear-gradient(rgba(232,53,46,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(232,53,46,.03) 1px,transparent 1px);background-size:60px 60px;pointer-events:none}
.bg-gradient{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse 80% 60% at 50% -20%,rgba(232,53,46,.08) 0%,transparent 60%);pointer-events:none}
.header{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 32px;height:64px;background:rgba(10,10,11,.85);backdrop-filter:blur(20px);border-bottom:1px solid var(--border)}
.logo{display:flex;align-items:center;gap:10px}
.logo-mark{display:flex;align-items:center;justify-content:center;width:36px;height:36px;background:var(--accent);color:#fff;font-family:var(--font-display);font-size:18px;letter-spacing:1px;border-radius:8px}
.logo-text{display:flex;flex-direction:column;line-height:1}
.logo-car{font-family:var(--font-display);font-size:20px;letter-spacing:3px;color:var(--text)}
.logo-sub{font-family:var(--font-mono);font-size:9px;letter-spacing:4px;color:var(--accent);text-transform:uppercase}
.nav-badge{font-family:var(--font-mono);font-size:11px;color:var(--text3);letter-spacing:1px;padding:4px 10px;border:1px solid var(--border);border-radius:20px}
.hero{position:relative;z-index:1;text-align:center;padding:80px 20px 60px;max-width:860px;margin:0 auto}
.hero-eyebrow{font-family:var(--font-mono);font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);margin-bottom:20px;display:inline-block;padding:6px 16px;border:1px solid rgba(232,53,46,.3);border-radius:20px;background:rgba(232,53,46,.05)}
.hero-title{font-family:var(--font-display);font-size:clamp(56px,12vw,110px);line-height:.92;letter-spacing:2px;margin-bottom:24px}
.title-line{display:block;color:var(--text)}.title-line.accent{color:var(--accent)}
.hero-sub{font-size:16px;color:var(--text2);line-height:1.7;max-width:560px;margin:0 auto 48px}
.search-card{background:var(--bg3);border:1px solid var(--border2);border-radius:20px;overflow:hidden;box-shadow:0 40px 80px rgba(0,0,0,.4)}
.tab-bar{display:flex;border-bottom:1px solid var(--border);background:var(--bg2)}
.tab{flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:14px 20px;background:none;border:none;cursor:pointer;font-family:var(--font-body);font-size:13px;font-weight:500;color:var(--text3);transition:all .2s;border-bottom:2px solid transparent}
.tab:hover{color:var(--text2)}.tab.active{color:var(--text);border-bottom-color:var(--accent)}
.tab-panel{display:none;padding:28px}.tab-panel.active{display:block}
.text-search-wrap{display:flex;gap:10px;background:var(--bg2);border:1px solid var(--border2);border-radius:var(--radius-sm);padding:6px 6px 6px 18px;transition:border-color .2s}
.text-search-wrap:focus-within{border-color:var(--accent)}
.text-input{flex:1;background:none;border:none;outline:none;font-family:var(--font-body);font-size:15px;color:var(--text);padding:10px 0}
.text-input::placeholder{color:var(--text3)}
.search-btn{display:flex;align-items:center;gap:8px;padding:12px 20px;background:var(--accent);border:none;border-radius:8px;cursor:pointer;font-family:var(--font-body);font-size:14px;font-weight:600;color:#fff;transition:all .2s;white-space:nowrap}
.search-btn:hover{background:#c42b25;transform:translateY(-1px)}
.search-btn.full{width:100%;justify-content:center;margin-top:16px;padding:16px}
.quick-chips{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:16px}
.chip-label{font-size:12px;color:var(--text3);font-weight:500}
.chip{padding:6px 14px;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:20px;cursor:pointer;font-family:var(--font-body);font-size:12px;color:var(--text2);transition:all .15s}
.chip:hover{background:rgba(232,53,46,.1);border-color:rgba(232,53,46,.3);color:var(--text)}
.drop-zone{border:2px dashed var(--border2);border-radius:var(--radius);padding:48px 24px;text-align:center;cursor:pointer;transition:all .2s}
.drop-zone:hover{border-color:var(--accent)}
.drop-icon{color:var(--text3);margin-bottom:16px}
.drop-title{font-size:15px;font-weight:500;color:var(--text2);margin-bottom:6px}
.drop-sub{font-size:12px;color:var(--text3)}
.preview-wrap{margin-top:16px;position:relative;display:inline-block}
.preview-img{max-height:200px;max-width:100%;border-radius:10px;display:block}
.clear-btn{position:absolute;top:-10px;right:-10px;background:var(--accent);color:#fff;border:none;border-radius:50%;width:28px;height:28px;cursor:pointer;font-size:11px}
.camera-wrap{border-radius:var(--radius);overflow:hidden;position:relative;background:#000}
.camera-video{width:100%;max-height:280px;display:block;object-fit:cover}
.camera-overlay{position:absolute;inset:0;pointer-events:none}
.camera-corner{position:absolute;width:24px;height:24px;border-color:var(--accent);border-style:solid;opacity:.8}
.camera-corner.tl{top:12px;left:12px;border-width:2px 0 0 2px}.camera-corner.tr{top:12px;right:12px;border-width:2px 2px 0 0}
.camera-corner.bl{bottom:12px;left:12px;border-width:0 0 2px 2px}.camera-corner.br{bottom:12px;right:12px;border-width:0 2px 2px 0}
.camera-captured{text-align:center;width:100%}
.retake-btn{margin-top:12px;background:var(--bg2);border:1px solid var(--border2);color:var(--text2);padding:8px 16px;border-radius:8px;cursor:pointer;font-size:13px;font-family:var(--font-body)}
.camera-controls{display:flex;gap:10px;justify-content:center;margin-top:16px;flex-wrap:wrap}
.cam-btn{display:flex;align-items:center;gap:8px;padding:12px 20px;background:var(--bg2);border:1px solid var(--border2);border-radius:var(--radius-sm);cursor:pointer;font-family:var(--font-body);font-size:14px;color:var(--text2);transition:all .2s}
.cam-btn:hover{border-color:var(--accent)}.cam-btn.snap{background:var(--accent);border-color:var(--accent);color:#fff}
.loading-overlay{position:fixed;inset:0;z-index:200;background:rgba(10,10,11,.9);backdrop-filter:blur(10px);display:flex;align-items:center;justify-content:center}
.loading-card{text-align:center}
.spinner-track{width:60px;height:60px;margin:0 auto 24px;border-radius:50%;border:2px solid rgba(255,255,255,.08);border-top-color:var(--accent);animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-msg{font-family:var(--font-display);font-size:28px;color:var(--text)}
.loading-sub{font-size:14px;color:var(--text3);margin-top:8px}
.results-section{position:relative;z-index:1;padding:60px 20px 80px}
.results-container{max-width:1100px;margin:0 auto}
.car-hero-banner{display:flex;align-items:center;justify-content:space-between;background:linear-gradient(135deg,#1a0e0d 0%,var(--bg3) 100%);border:1px solid rgba(232,53,46,.15);border-radius:24px;padding:48px;margin-bottom:28px;position:relative;gap:32px}
.car-hero-banner::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(232,53,46,.5),transparent)}
.car-hero-content{flex:1}
.car-badge{display:inline-block;font-family:var(--font-mono);font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--accent);padding:5px 12px;border:1px solid rgba(232,53,46,.3);border-radius:20px;margin-bottom:16px}
.car-hero-name{font-family:var(--font-display);font-size:clamp(36px,6vw,64px);line-height:.95;color:var(--text);margin-bottom:12px}
.car-hero-tagline{font-size:15px;color:var(--text2);margin-bottom:20px;font-style:italic}
.car-meta-row{display:flex;flex-wrap:wrap;gap:8px}
.meta-chip{font-family:var(--font-mono);font-size:12px;padding:5px 12px;background:rgba(255,255,255,.05);border:1px solid var(--border);border-radius:20px;color:var(--text2)}
.meta-chip.highlight{background:rgba(201,168,76,.1);border-color:rgba(201,168,76,.3);color:var(--gold)}
.car-image-area{flex-shrink:0}
.car-image-placeholder{width:160px;height:120px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:16px;font-family:var(--font-display);font-size:40px;color:var(--text3)}
.results-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.result-card{background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--radius);padding:28px;animation:fadeUp .5s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.result-card:nth-child(1){animation-delay:.05s}.result-card:nth-child(2){animation-delay:.1s}.result-card:nth-child(3){animation-delay:.15s}.result-card:nth-child(4){animation-delay:.2s}.result-card:nth-child(5){animation-delay:.25s}.result-card:nth-child(6){animation-delay:.3s}.result-card:nth-child(7){animation-delay:.35s}.result-card:nth-child(8){animation-delay:.4s}
.card-head{display:flex;align-items:center;gap:10px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.card-icon{width:32px;height:32px;display:flex;align-items:center;justify-content:center;background:rgba(232,53,46,.1);border:1px solid rgba(232,53,46,.2);border-radius:8px;font-size:14px;color:var(--accent)}
.card-head h3{font-size:15px;font-weight:600;color:var(--text);flex:1}
.card-note{font-size:11px;color:var(--text3);font-family:var(--font-mono)}
.pricing-range{margin-bottom:20px;padding:16px;background:rgba(201,168,76,.05);border:1px solid rgba(201,168,76,.15);border-radius:var(--radius-sm);text-align:center}
.price-from-to{font-family:var(--font-display);font-size:28px;color:var(--gold)}
.price-label{font-size:11px;color:var(--text3);margin-top:4px;font-family:var(--font-mono)}
.variants-list{display:flex;flex-direction:column;gap:8px;max-height:280px;overflow-y:auto}
.variant-row{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:8px}
.variant-name{font-size:13px;color:var(--text2);flex:1}
.variant-fuel{font-family:var(--font-mono);font-size:10px;padding:3px 8px;border-radius:10px;margin:0 10px}
.fuel-petrol{background:rgba(255,107,53,.1);color:#ff6b35;border:1px solid rgba(255,107,53,.2)}
.fuel-diesel{background:rgba(52,152,219,.1);color:#3498db;border:1px solid rgba(52,152,219,.2)}
.fuel-electric{background:rgba(46,204,113,.1);color:var(--green);border:1px solid rgba(46,204,113,.2)}
.fuel-cng{background:rgba(155,89,182,.1);color:#9b59b6;border:1px solid rgba(155,89,182,.2)}
.variant-price{font-family:var(--font-mono);font-size:13px;font-weight:500;color:var(--text)}
.specs-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.spec-item{padding:12px;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:8px}
.spec-label{font-size:11px;color:var(--text3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}
.spec-value{font-size:14px;font-weight:600;color:var(--text)}
.colors-grid{display:flex;flex-wrap:wrap;gap:14px}
.color-swatch{display:flex;flex-direction:column;align-items:center;gap:8px}
.swatch-circle{width:44px;height:44px;border-radius:50%;border:2px solid rgba(255,255,255,.1);box-shadow:0 4px 12px rgba(0,0,0,.4);transition:transform .2s;position:relative}
.swatch-circle:hover{transform:scale(1.1)}
.swatch-name{font-size:10px;color:var(--text3);text-align:center;max-width:60px;line-height:1.3}
.features-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px}
.feature-tab{padding:5px 12px;border-radius:20px;cursor:pointer;font-size:12px;font-weight:500;background:rgba(255,255,255,.04);border:1px solid var(--border);color:var(--text3);transition:all .15s}
.feature-tab.active{background:rgba(232,53,46,.1);border-color:rgba(232,53,46,.3);color:var(--text)}
.features-list{display:flex;flex-direction:column;gap:8px}
.feature-item{display:flex;align-items:flex-start;gap:10px;font-size:13px;color:var(--text2);line-height:1.4}
.feature-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);flex-shrink:0;margin-top:5px}
.interior-info{display:flex;flex-direction:column;gap:14px}
.interior-stat{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}
.interior-stat:last-child{border-bottom:none}
.int-label{font-size:12px;color:var(--text3);font-family:var(--font-mono)}
.int-value{font-size:13px;font-weight:500;color:var(--text)}
.quality-badge{padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;text-transform:uppercase}
.quality-premium{background:rgba(201,168,76,.1);color:var(--gold);border:1px solid rgba(201,168,76,.2)}
.quality-good{background:rgba(46,204,113,.1);color:var(--green);border:1px solid rgba(46,204,113,.2)}
.quality-average{background:rgba(52,152,219,.1);color:#3498db;border:1px solid rgba(52,152,219,.2)}
.quality-budget{background:rgba(255,255,255,.05);color:var(--text3);border:1px solid var(--border)}
.interior-highlights{margin-top:16px;display:flex;flex-direction:column;gap:8px}
.proscons-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.pros-col,.cons-col{display:flex;flex-direction:column;gap:8px}
.pros-head,.cons-head{font-size:11px;font-family:var(--font-mono);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px}
.pros-head{color:var(--green)}.cons-head{color:var(--red)}
.pro-item,.con-item{display:flex;align-items:flex-start;gap:8px;font-size:13px;line-height:1.4;color:var(--text2)}
.pro-icon{color:var(--green);flex-shrink:0}.con-icon{color:var(--red);flex-shrink:0}
.competitors-list{display:flex;flex-direction:column;gap:12px}
.competitor-card{padding:14px;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:10px}
.comp-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.comp-name{font-size:14px;font-weight:600;color:var(--text)}
.comp-price{font-family:var(--font-mono);font-size:12px;color:var(--gold)}
.comp-reason{font-size:12px;color:var(--text3);line-height:1.4}
.verdict-content{margin-bottom:20px}
.verdict-pick{background:linear-gradient(135deg,rgba(232,53,46,.08),rgba(232,53,46,.03));border:1px solid rgba(232,53,46,.15);border-radius:var(--radius-sm);padding:16px;margin-bottom:16px}
.verdict-pick-label{font-size:11px;color:var(--accent);font-family:var(--font-mono);letter-spacing:2px;margin-bottom:8px}
.verdict-pick-text{font-size:14px;color:var(--text);line-height:1.5}
.target-row{display:flex;align-items:center;gap:10px;padding:12px;background:rgba(255,255,255,.02);border-radius:8px}
.target-label{font-size:11px;color:var(--text3);font-family:var(--font-mono);white-space:nowrap}
.target-text{font-size:13px;color:var(--text2)}
.facts-list{margin-top:16px;display:flex;flex-direction:column;gap:8px}
.fact-item{display:flex;gap:10px;align-items:flex-start;font-size:13px;color:var(--text2);line-height:1.4}
.fact-num{font-family:var(--font-mono);font-size:11px;color:var(--accent);width:20px;flex-shrink:0}
.card-features{grid-column:1 / -1}.card-verdict{grid-column:1 / -1}
.reset-wrap{text-align:center;margin-top:48px}
.reset-btn{display:inline-flex;align-items:center;gap:10px;padding:14px 28px;background:transparent;border:1px solid var(--border2);border-radius:30px;cursor:pointer;font-family:var(--font-body);font-size:14px;color:var(--text2);transition:all .2s}
.reset-btn:hover{border-color:var(--accent);color:var(--text)}
.footer{position:relative;z-index:1;text-align:center;padding:24px;border-top:1px solid var(--border);font-size:12px;color:var(--text3);font-family:var(--font-mono)}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px}
@media(max-width:600px){.header{padding:0 16px}.hero{padding:48px 16px 40px}.tab-panel{padding:20px}.car-hero-banner{flex-direction:column;padding:28px 20px}.car-image-area{display:none}.results-grid{grid-template-columns:1fr}.card-features,.card-verdict{grid-column:1}.proscons-grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
<div class="bg-grid"></div><div class="bg-gradient"></div>
<header class="header">
  <div class="logo"><span class="logo-mark">IQ</span><div class="logo-text"><span class="logo-car">CAR</span><span class="logo-sub">INDIA</span></div></div>
  <nav><span class="nav-badge">Powered by Claude AI</span></nav>
</header>
<section class="hero" id="hero">
  <div class="hero-eyebrow">India's Most Intelligent Car Research Tool</div>
  <h1 class="hero-title"><span class="title-line">EVERY CAR.</span><span class="title-line accent">EVERY DETAIL.</span></h1>
  <p class="hero-sub">Upload a photo, snap with camera, or type a car name. Get instant AI-powered insights &mdash; prices, specs, colors, features &amp; more.</p>
  <div class="search-card">
    <div class="tab-bar">
      <button class="tab active" data-tab="text" onclick="switchTab('text')"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>Search by Name</button>
      <button class="tab" data-tab="upload" onclick="switchTab('upload')"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>Upload Image</button>
      <button class="tab" data-tab="camera" onclick="switchTab('camera')"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>Camera</button>
    </div>
    <div class="tab-panel active" id="panel-text">
      <div class="text-search-wrap">
        <input type="text" class="text-input" id="textInput" placeholder="e.g. Tata Nexon EV, Maruti Swift ZXi+, Hyundai Creta..." autocomplete="off"/>
        <button class="search-btn" onclick="searchByText()"><span>Analyse</span><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg></button>
      </div>
      <div class="quick-chips">
        <span class="chip-label">Popular:</span>
        <button class="chip" onclick="quickSearch('Tata Nexon EV')">Nexon EV</button>
        <button class="chip" onclick="quickSearch('Maruti Suzuki Swift 2024')">Swift 2024</button>
        <button class="chip" onclick="quickSearch('Hyundai Creta 2024')">Creta 2024</button>
        <button class="chip" onclick="quickSearch('Mahindra XEV 9e')">XEV 9e</button>
        <button class="chip" onclick="quickSearch('Kia Syros')">Kia Syros</button>
      </div>
    </div>
    <div class="tab-panel" id="panel-upload">
      <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()" ondragover="handleDragOver(event)" ondrop="handleDrop(event)">
        <div class="drop-icon"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg></div>
        <p class="drop-title">Drop your car image here</p>
        <p class="drop-sub">or click to browse &mdash; JPG, PNG, WEBP</p>
        <div class="preview-wrap" id="previewWrap" style="display:none"><img id="previewImg" class="preview-img" alt=""/><button class="clear-btn" onclick="clearImage(event)">x</button></div>
      </div>
      <input type="file" id="fileInput" accept="image/*" style="display:none" onchange="handleFileSelect(event)"/>
      <button class="search-btn full" id="analyzeUploadBtn" onclick="analyzeUploadedImage()" style="display:none">Analyse This Car</button>
    </div>
    <div class="tab-panel" id="panel-camera">
      <div class="camera-wrap" id="cameraWrap"><video id="cameraVideo" class="camera-video" autoplay playsinline></video><canvas id="cameraCanvas" style="display:none"></canvas><div class="camera-overlay"><div class="camera-corner tl"></div><div class="camera-corner tr"></div><div class="camera-corner bl"></div><div class="camera-corner br"></div></div></div>
      <div class="camera-captured" id="cameraCaptured" style="display:none"><img id="capturedImg" class="preview-img" alt=""/><br/><button class="retake-btn" onclick="retakePhoto()">Retake</button></div>
      <div class="camera-controls">
        <button class="cam-btn" id="startCamBtn" onclick="startCamera()">Start Camera</button>
        <button class="cam-btn snap" id="snapBtn" onclick="capturePhoto()" style="display:none">Capture</button>
        <button class="search-btn" id="analyzeCamBtn" onclick="analyzeCaptured()" style="display:none">Analyse</button>
      </div>
    </div>
  </div>
</section>
<div class="loading-overlay" id="loadingOverlay" style="display:none"><div class="loading-card"><div class="spinner-track"></div><p class="loading-msg" id="loadingMsg">Identifying your car...</p><p class="loading-sub">Scanning specs, prices &amp; features</p></div></div>
<section class="results-section" id="resultsSection" style="display:none">
  <div class="results-container">
    <div class="car-hero-banner">
      <div class="car-hero-content"><div class="car-badge" id="carBadge"></div><h2 class="car-hero-name" id="carHeroName"></h2><p class="car-hero-tagline" id="carHeroTagline"></p><div class="car-meta-row"><span class="meta-chip" id="metaBodyType"></span><span class="meta-chip" id="metaYearRange"></span><span class="meta-chip highlight" id="metaPriceRange"></span></div></div>
      <div class="car-image-area"><div class="car-image-placeholder"><span id="carInitials"></span></div></div>
    </div>
    <div class="results-grid">
      <div class="result-card card-pricing"><div class="card-head"><div class="card-icon">Rs</div><h3>Pricing</h3><span class="card-note">Ex-showroom, Delhi</span></div><div class="pricing-range" id="pricingRange"></div><div class="variants-list" id="variantsList"></div></div>
      <div class="result-card card-specs"><div class="card-head"><div class="card-icon">--</div><h3>Specifications</h3></div><div class="specs-grid" id="specsGrid"></div></div>
      <div class="result-card card-colors"><div class="card-head"><div class="card-icon">[]</div><h3>Available Colors</h3></div><div class="colors-grid" id="colorsGrid"></div></div>
      <div class="result-card card-features"><div class="card-head"><div class="card-icon">*</div><h3>Key Features</h3></div><div class="features-tabs" id="featuresTabs"></div><div class="features-list" id="featuresList"></div></div>
      <div class="result-card card-interior"><div class="card-head"><div class="card-icon">~</div><h3>Interior</h3></div><div class="interior-info" id="interiorInfo"></div></div>
      <div class="result-card card-proscons"><div class="card-head"><div class="card-icon">+-</div><h3>Pros &amp; Cons</h3></div><div class="proscons-grid" id="prosConsGrid"></div></div>
      <div class="result-card card-competitors"><div class="card-head"><div class="card-icon">vs</div><h3>Vs. Competition</h3></div><div class="competitors-list" id="competitorsList"></div></div>
      <div class="result-card card-verdict"><div class="card-head"><div class="card-icon">!</div><h3>CarIQ Verdict</h3></div><div class="verdict-content" id="verdictContent"></div><div class="facts-list" id="factsList"></div></div>
    </div>
    <div class="reset-wrap"><button class="reset-btn" onclick="resetApp()">Search Another Car</button></div>
  </div>
</section>
<footer class="footer"><p>CarIQ India &mdash; AI-powered car intelligence for Indian buyers &mdash; Prices indicative, verify with dealer</p></footer>
<script>
let capturedImageData=null,uploadedImageData=null,cameraStream=null,currentFeaturesData=null,loadingTimer=null;
function switchTab(t){document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.querySelectorAll('.tab-panel').forEach(e=>e.classList.remove('active'));document.querySelector('[data-tab="'+t+'"]').classList.add('active');document.getElementById('panel-'+t).classList.add('active');if(t!=='camera'&&cameraStream)stopCamera();}
function quickSearch(q){document.getElementById('textInput').value=q;searchByText();}
async function searchByText(){const q=document.getElementById('textInput').value.trim();if(!q)return;await doAnalyze('/api/analyze/text',{query:q});}
document.addEventListener('DOMContentLoaded',()=>{document.getElementById('textInput').addEventListener('keydown',e=>{if(e.key==='Enter')searchByText();});});
function handleDragOver(e){e.preventDefault();}
function handleDrop(e){e.preventDefault();const f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))processFile(f);}
function handleFileSelect(e){const f=e.target.files[0];if(f)processFile(f);}
function processFile(f){const r=new FileReader();r.onload=ev=>{uploadedImageData=ev.target.result;document.getElementById('previewImg').src=uploadedImageData;document.getElementById('previewWrap').style.display='block';document.querySelector('.drop-icon').style.display='none';document.querySelector('.drop-title').style.display='none';document.querySelector('.drop-sub').style.display='none';document.getElementById('analyzeUploadBtn').style.display='flex';};r.readAsDataURL(f);}
function clearImage(e){e.stopPropagation();uploadedImageData=null;document.getElementById('previewWrap').style.display='none';document.querySelector('.drop-icon').style.display='block';document.querySelector('.drop-title').style.display='block';document.querySelector('.drop-sub').style.display='block';document.getElementById('analyzeUploadBtn').style.display='none';document.getElementById('fileInput').value='';}
async function analyzeUploadedImage(){if(uploadedImageData)await doAnalyze('/api/analyze/image',{image:uploadedImageData});}
async function startCamera(){try{cameraStream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment',width:{ideal:1280},height:{ideal:720}}});document.getElementById('cameraVideo').srcObject=cameraStream;document.getElementById('startCamBtn').style.display='none';document.getElementById('snapBtn').style.display='flex';}catch(err){alert('Camera access denied. Please use file upload instead.');}}
function capturePhoto(){const v=document.getElementById('cameraVideo'),c=document.getElementById('cameraCanvas');c.width=v.videoWidth;c.height=v.videoHeight;c.getContext('2d').drawImage(v,0,0);capturedImageData=c.toDataURL('image/jpeg',.92);document.getElementById('capturedImg').src=capturedImageData;document.getElementById('cameraWrap').style.display='none';document.getElementById('cameraCaptured').style.display='block';document.getElementById('snapBtn').style.display='none';document.getElementById('analyzeCamBtn').style.display='flex';stopCamera();}
function retakePhoto(){capturedImageData=null;document.getElementById('cameraCaptured').style.display='none';document.getElementById('analyzeCamBtn').style.display='none';document.getElementById('startCamBtn').style.display='flex';document.getElementById('cameraWrap').style.display='block';startCamera();}
function stopCamera(){if(cameraStream){cameraStream.getTracks().forEach(t=>t.stop());cameraStream=null;}}
async function analyzeCaptured(){if(capturedImageData)await doAnalyze('/api/analyze/image',{image:capturedImageData});}
const msgs=['Identifying your car...','Scanning Indian market prices...','Fetching variants & colors...','Pulling specs & features...','Preparing your CarIQ report...'];
function showLoading(){document.getElementById('loadingOverlay').style.display='flex';let i=0;document.getElementById('loadingMsg').textContent=msgs[0];loadingTimer=setInterval(()=>{i=(i+1)%msgs.length;document.getElementById('loadingMsg').textContent=msgs[i];},1800);}
function hideLoading(){clearInterval(loadingTimer);document.getElementById('loadingOverlay').style.display='none';}
async function doAnalyze(url,payload){showLoading();try{const res=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const r=await res.json();if(!res.ok||!r.success)throw new Error(r.error||'Analysis failed');hideLoading();render(r.data);}catch(err){hideLoading();alert('Error: '+err.message);}}
function h(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function render(d){
  document.getElementById('hero').style.display='none';
  document.getElementById('resultsSection').style.display='block';
  window.scrollTo({top:0,behavior:'smooth'});
  document.getElementById('carBadge').textContent=(d.brand||'')+' - '+(d.body_type||'');
  document.getElementById('carHeroName').textContent=d.car_name||d.model||'Unknown Car';
  document.getElementById('carHeroTagline').textContent=d.tagline||'';
  document.getElementById('metaBodyType').textContent=d.body_type||'';
  document.getElementById('metaYearRange').textContent=d.year_range||'';
  const pf=d.pricing&&d.pricing.base_variant||'',pt=d.pricing&&d.pricing.top_variant||'';
  document.getElementById('metaPriceRange').textContent=pf&&pt?pf+' - '+pt:pf||pt||'';
  const nm=d.car_name||d.model||'?';
  document.getElementById('carInitials').textContent=nm.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase();
  const p=d.pricing||{};
  document.getElementById('pricingRange').innerHTML=(p.base_variant||p.top_variant)?'<div class="price-from-to">'+h(p.base_variant||'')+(p.base_variant&&p.top_variant?' - ':'')+h(p.top_variant||'')+'</div><div class="price-label">Starting Price - Ex-showroom Delhi</div>':'';
  document.getElementById('variantsList').innerHTML=(p.variants||[]).map(v=>'<div class="variant-row"><span class="variant-name">'+h(v.name||'')+'</span><span class="variant-fuel fuel-'+(v.fuel||'').toLowerCase()+'">'+h(v.fuel||'')+'</span><span class="variant-price">'+h(v.price||'')+'</span></div>').join('');
  const s=d.specifications||{};
  const sm=[['Engine','engine'],['Power','power'],['Torque','torque'],['Transmission','transmission'],['Mileage (ARAI)','mileage_arai'],['0-100 km/h','0_to_100'],['Fuel Tank','fuel_tank'],['Boot Space','boot_space']];
  document.getElementById('specsGrid').innerHTML=sm.filter(i=>s[i[1]]).map(i=>'<div class="spec-item"><div class="spec-label">'+i[0]+'</div><div class="spec-value">'+h(s[i[1]])+'</div></div>').join('');
  document.getElementById('colorsGrid').innerHTML=(d.colors||[]).map(c=>'<div class="color-swatch"><div class="swatch-circle" style="background:'+h(c.hex||'#888')+'" title="'+h(c.name||'')+'"></div><span class="swatch-name">'+h(c.name||'')+'</span></div>').join('');
  currentFeaturesData=d.features||{};
  const cats=['safety','comfort','technology','infotainment'];
  document.getElementById('featuresTabs').innerHTML=cats.filter(c=>currentFeaturesData[c]&&currentFeaturesData[c].length).map(c=>'<button class="feature-tab'+(c==='safety'?' active':'')+'" onclick="showF(\''+c+'\',this)">'+c.charAt(0).toUpperCase()+c.slice(1)+'</button>').join('');
  showF('safety',null);
  const it=d.interior||{},qc=(it.quality||'average').toLowerCase();
  document.getElementById('interiorInfo').innerHTML=[['QUALITY','<span class="quality-badge quality-'+qc+'">'+h(it.quality||'N/A')+'</span>'],['SEATING',h(it.seating||'N/A')],['SCREEN SIZE',h(it.screen_size||'N/A')],['UPHOLSTERY',h(it.upholstery||'N/A')]].map(x=>'<div class="interior-stat"><span class="int-label">'+x[0]+'</span><span class="int-value">'+x[1]+'</span></div>').join('')+((it.highlights&&it.highlights.length)?'<div class="interior-highlights">'+it.highlights.map(x=>'<div class="feature-item"><div class="feature-dot"></div><span>'+h(x)+'</span></div>').join('')+'</div>':'');
  document.getElementById('prosConsGrid').innerHTML='<div class="pros-col"><div class="pros-head">PROS</div>'+(d.pros||[]).map(x=>'<div class="pro-item"><span class="pro-icon">+</span><span>'+h(x)+'</span></div>').join('')+'</div><div class="cons-col"><div class="cons-head">CONS</div>'+(d.cons||[]).map(x=>'<div class="con-item"><span class="con-icon">-</span><span>'+h(x)+'</span></div>').join('')+'</div>';
  document.getElementById('competitorsList').innerHTML=(d.competitors||[]).map(c=>'<div class="competitor-card"><div class="comp-top"><span class="comp-name">'+h(c.name||'')+'</span><span class="comp-price">'+h(c.price_range||'')+'</span></div><div class="comp-reason">'+h(c.advantage||'')+'</div></div>').join('');
  document.getElementById('verdictContent').innerHTML=(d.best_variant_pick?'<div class="verdict-pick"><div class="verdict-pick-label">BEST VARIANT PICK</div><div class="verdict-pick-text">'+h(d.best_variant_pick)+'</div></div>':'')+(d.target_buyer?'<div class="target-row"><span class="target-label">IDEAL FOR</span><span class="target-text">'+h(d.target_buyer)+'</span></div>':'');
  document.getElementById('factsList').innerHTML=(d.interesting_facts||[]).map((f,i)=>'<div class="fact-item"><span class="fact-num">0'+(i+1)+'</span><span>'+h(f)+'</span></div>').join('');
}
function showF(cat,btn){if(btn){document.querySelectorAll('.feature-tab').forEach(t=>t.classList.remove('active'));btn.classList.add('active');}document.getElementById('featuresList').innerHTML=((currentFeaturesData&&currentFeaturesData[cat])||[]).map(f=>'<div class="feature-item"><div class="feature-dot"></div><span>'+h(f)+'</span></div>').join('');}
function resetApp(){document.getElementById('hero').style.display='block';document.getElementById('resultsSection').style.display='none';document.getElementById('textInput').value='';uploadedImageData=null;capturedImageData=null;switchTab('text');window.scrollTo({top:0,behavior:'smooth'});}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return Response(HTML_PAGE, mimetype="text/html")


@app.route("/api/analyze/image", methods=["POST"])
def analyze_image():
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image provided"}), 400
        image_data = data["image"]
        if "," in image_data:
            header, image_base64 = image_data.split(",", 1)
            media_type = header.split(":")[1].split(";")[0]
        else:
            image_base64 = image_data
            media_type = "image/jpeg"
        result = analyze_car_image(image_base64, media_type)
        return jsonify({"success": True, "data": result})
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse car data", "details": str(e)}), 500
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
        return jsonify({"error": "Failed to parse car data", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "CarIQ India"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
