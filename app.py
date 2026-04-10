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

CAR_PROMPT = """You are an expert on cars sold in India. Return ONLY a JSON object, no markdown, no explanation.

JSON structure:
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
    "transmission": "Manual / AMT",
    "mileage_arai": "18.76 kmpl",
    "0_to_100": "11.2 sec",
    "fuel_tank": "37 litres",
    "boot_space": "308 litres"
  },
  "features": {
    "safety": ["6 Airbags"],
    "comfort": ["Sunroof"],
    "technology": ["ADAS"],
    "infotainment": ["10.25-inch touchscreen"]
  },
  "interior": {
    "quality": "Good",
    "screen_size": "10.25-inch",
    "seating": "5-seater",
    "upholstery": "Leatherette",
    "highlights": ["Ambient lighting"]
  },
  "pros": ["Spacious cabin", "Good mileage"],
  "cons": ["Average ride quality"],
  "competitors": [
    {"name": "Hyundai Venue", "price_range": "Rs 7.94-13.35 Lakh", "advantage": "Better resale value"}
  ],
  "interesting_facts": ["Best-selling compact SUV in 2023"],
  "best_variant_pick": "Mid variant offers best value",
  "target_buyer": "Young families",
  "confidence": "high"
}

Start response with { and end with }. No other text."""


def clean_json(text):
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    return json.loads(text)


def call_claude(messages):
    """Single Claude call with streaming to reduce memory."""
    full_text = ""
    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system=CAR_PROMPT,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            full_text += text
    return clean_json(full_text)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/analyze/text", methods=["POST"])
def api_text():
    try:
        body = request.get_json()
        if not body or not body.get("query"):
            return jsonify({"success": False, "error": "No query provided"}), 400
        data = call_claude([{"role": "user", "content": "Car: " + body["query"]}])
        data["images"] = []
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print("ERROR:", str(e), flush=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/analyze/image", methods=["POST"])
def api_image():
    try:
        body = request.get_json()
        if not body or not body.get("image"):
            return jsonify({"success": False, "error": "No image provided"}), 400
        img = body["image"]
        if "," in img:
            header, b64 = img.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
        else:
            b64, mime = img, "image/jpeg"
        # Resize large images to reduce memory — cap base64 size
        if len(b64) > 1_000_000:  # > ~750KB image
            return jsonify({"success": False, "error": "Image too large. Please use a smaller photo (under 1MB)."}), 400
        data = call_claude([{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
            {"type": "text", "text": "Identify this car."}
        ]}])
        data["images"] = []
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print("ERROR:", str(e), flush=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
