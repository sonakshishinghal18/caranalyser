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

CAR_PROMPT = """You are an expert on cars sold in India. Given a car name or image, return ONLY a JSON object with no extra text, no markdown fences, no explanation.

Return this exact JSON structure:
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
  "interesting_facts": ["Fact 1", "Fact 2"],
  "best_variant_pick": "Mid variant XZ+ offers best value",
  "target_buyer": "Young families and first-time SUV buyers",
  "confidence": "high"
}

IMPORTANT: Output ONLY the raw JSON. No markdown. No backticks. No explanation. Start your response with { and end with }"""


def clean_json(text):
    """Robustly extract JSON from Claude response."""
    text = text.strip()
    # Strip markdown code fences
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    # Find the first { and last } to extract JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    return json.loads(text)


def call_claude_text(query):
    r = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=CAR_PROMPT,
        messages=[{"role": "user", "content": "Provide complete details for this car: " + query}]
    )
    raw = r.content[0].text
    print("CAR TEXT RAW (first 200):", raw[:200], flush=True)
    return clean_json(raw)


def call_claude_image(b64, mime):
    r = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=CAR_PROMPT,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
            {"type": "text", "text": "Identify this car and provide complete details."}
        ]}]
    )
    raw = r.content[0].text
    print("CAR IMAGE RAW (first 200):", raw[:200], flush=True)
    return clean_json(raw)


def fetch_images_via_claude(car_name):
    """Use Claude with web_search to find real car image URLs."""
    try:
        r = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    "Search for photos of " + car_name + " car in India. "
                    "Find direct image URLs (.jpg or .png files) from cardekho.com, carwale.com, or zigwheels.com. "
                    "Return ONLY a JSON array like: "
                    '[{"url":"https://...jpg","title":"...","type":"exterior"}] '
                    "Include 3 exterior and 2 interior photos. "
                    "Only include URLs that end in .jpg .jpeg .png .webp"
                )
            }]
        )
        # Collect all text blocks from response
        text_parts = []
        for block in r.content:
            if hasattr(block, "text") and block.text:
                text_parts.append(block.text)
        text = " ".join(text_parts).strip()
        print("IMAGE RAW (first 300):", text[:300], flush=True)

        # Extract JSON array from response
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or end <= start:
            print("IMAGE: no array found", flush=True)
            return []
        arr_text = text[start:end+1]
        result = json.loads(arr_text)
        if not isinstance(result, list):
            return []
        # Filter to valid image URLs only
        valid = []
        for img in result:
            url = img.get("url", "")
            if url and re.search(r"\.(jpg|jpeg|png|webp)(\?.*)?$", url, re.IGNORECASE):
                valid.append({
                    "url":   url,
                    "title": img.get("title", car_name),
                    "type":  img.get("type", "exterior")
                })
        print("IMAGE: valid count =", len(valid), flush=True)
        return valid[:6]
    except Exception as e:
        print("IMAGE ERROR:", str(e), flush=True)
        return []


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/analyze/text", methods=["POST"])
def api_text():
    try:
        body = request.get_json()
        if not body or not body.get("query"):
            return jsonify({"success": False, "error": "No query provided"}), 400
        data = call_claude_text(body["query"])
        data["images"] = fetch_images_via_claude(data.get("car_name") or body["query"])
        return jsonify({"success": True, "data": data})
    except json.JSONDecodeError as e:
        print("JSON PARSE ERROR:", str(e), flush=True)
        return jsonify({"success": False, "error": "Could not parse car data. Please try again."}), 500
    except Exception as e:
        print("API ERROR:", str(e), flush=True)
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
        data = call_claude_image(b64, mime)
        data["images"] = fetch_images_via_claude(data.get("car_name") or "car")
        return jsonify({"success": True, "data": data})
    except json.JSONDecodeError as e:
        print("JSON PARSE ERROR:", str(e), flush=True)
        return jsonify({"success": False, "error": "Could not parse car data. Please try again."}), 500
    except Exception as e:
        print("API ERROR:", str(e), flush=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
