import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

PROMPT = """You are an expert on cars sold in India. Given a car name or image, return ONLY a JSON object with no extra text, no markdown fences.

JSON format:
{
  "car_name": "Full name",
  "brand": "Brand",
  "model": "Model",
  "tagline": "One catchy line",
  "year_range": "2023-2025",
  "body_type": "SUV",
  "colors": [{"name": "Pearl White", "hex": "#f5f5f5", "type": "pearl"}],
  "pricing": {
    "base_variant": "Rs 8.00 Lakh",
    "top_variant": "Rs 15.00 Lakh",
    "variants": [{"name": "Base E", "price": "Rs 8.00 Lakh", "fuel": "Petrol"}]
  },
  "specifications": {
    "engine": "1.2L Turbo",
    "power": "100 bhp",
    "torque": "170 Nm",
    "transmission": "6-speed Manual / AMT",
    "mileage_arai": "18.76 kmpl",
    "0_to_100": "11.2 sec",
    "fuel_tank": "37 litres",
    "boot_space": "308 litres"
  },
  "features": {
    "safety": ["6 Airbags", "ESC"],
    "comfort": ["Ventilated seats", "Sunroof"],
    "technology": ["ADAS Level 2", "OTA updates"],
    "infotainment": ["10.25-inch touchscreen", "Wireless Android Auto"]
  },
  "interior": {
    "quality": "Good",
    "screen_size": "10.25-inch",
    "seating": "5-seater",
    "upholstery": "Leatherette",
    "highlights": ["Dual-tone dashboard", "Ambient lighting"]
  },
  "pros": ["Spacious cabin", "Feature-loaded", "Good mileage"],
  "cons": ["Average ride quality", "No diesel option"],
  "competitors": [
    {"name": "Hyundai Venue", "price_range": "Rs 7.94-13.35 Lakh", "advantage": "Better resale value"}
  ],
  "interesting_facts": ["Best-selling compact SUV in 2023", "Over 5 lakh units sold"],
  "best_variant_pick": "Mid variant XZ+ offers best value",
  "target_buyer": "Young families and first-time SUV buyers",
  "confidence": "high"
}

Important: prices in Rs X.XX Lakh format. Return ONLY the JSON."""


def call_claude_image(b64, mime):
    r = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=PROMPT,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
            {"type": "text", "text": "Identify this car and return JSON only."}
        ]}]
    )
    return clean_json(r.content[0].text)


def call_claude_text(query):
    r = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=PROMPT,
        messages=[{"role": "user", "content": "Car: " + query + ". Return JSON only."}]
    )
    return clean_json(r.content[0].text)


def clean_json(text):
    text = text.strip()
    text = re.sub(r"^```[a-z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/analyze/text", methods=["POST"])
def api_text():
    try:
        body = request.get_json()
        if not body or not body.get("query"):
            return jsonify({"success": False, "error": "No query"}), 400
        data = call_claude_text(body["query"])
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/analyze/image", methods=["POST"])
def api_image():
    try:
        body = request.get_json()
        if not body or not body.get("image"):
            return jsonify({"success": False, "error": "No image"}), 400
        img = body["image"]
        if "," in img:
            header, b64 = img.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
        else:
            b64, mime = img, "image/jpeg"
        data = call_claude_image(b64, mime)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
