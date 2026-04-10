import os
import base64
import json
import re
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import anthropic

app = Flask(__name__, static_folder="static", template_folder="templates")
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
    "base_variant": "₹X.XX Lakh",
    "top_variant": "₹X.XX Lakh",
    "variants": [
      {"name": "Variant Name", "price": "₹X.XX Lakh", "fuel": "Petrol/Diesel/CNG/Electric"}
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
    {"name": "Car Name", "price_range": "₹X-Y Lakh", "advantage": "Why someone might pick this instead"}
  ],
  "interesting_facts": ["Fact 1", "Fact 2", "Fact 3"],
  "best_variant_pick": "Recommended variant with reason",
  "target_buyer": "Who should buy this car",
  "image_search_query": "A precise Google Images search query to find good photos of this car in India",
  "confidence": "high/medium/low"
}

IMPORTANT: 
- All prices must be in Indian Rupees (₹) and in Lakh format
- Be accurate with Indian market pricing
- If you cannot identify the car from an image, set confidence to "low" and provide best guess
- Always return valid JSON only, no markdown, no extra text
- For colors, provide approximate hex codes that match the actual car color"""


def analyze_car_image(image_base64: str, media_type: str) -> dict:
    """Analyze car from image using Claude Vision."""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=CAR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Identify this car and provide complete information for an Indian buyer. Return JSON only."
                    }
                ],
            }
        ],
    )
    return parse_car_response(message.content[0].text)


def analyze_car_text(car_name: str) -> dict:
    """Analyze car from text name/description."""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system=CAR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Provide complete information for: {car_name}. Return JSON only."
            }
        ],
    )
    return parse_car_response(message.content[0].text)


def parse_car_response(text: str) -> dict:
    """Parse JSON response from Claude."""
    text = text.strip()
    # Strip markdown code blocks if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()
    return json.loads(text)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze/image", methods=["POST"])
def analyze_image():
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image provided"}), 400

        image_data = data["image"]
        # Handle data URL format: data:image/jpeg;base64,....
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
