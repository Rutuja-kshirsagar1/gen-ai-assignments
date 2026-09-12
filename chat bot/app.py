import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env (used only for LOCAL development)
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Set it in a .env file (local) "
        "or as an environment variable / secret (deployment)."
    )

genai.configure(api_key=API_KEY)

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2python app.py.0-flash")

SYSTEM_PROMPT = """You are FoodieBot, a friendly assistant for an online food ordering service.
You help customers with:
- Browsing the menu and recommending items
- Placing, modifying, or cancelling orders
- Answering questions about order status, delivery time, and payment
- Handling complaints (wrong item, late delivery, cold food, missing item, refund requests)
  with empathy, and clearly explaining the next step (e.g. "I've logged a refund request,
  our team will confirm within 24 hours").
- General food-safety / allergy questions (always advise checking with the restaurant for
  severe allergies).

Keep replies short, warm, and practical. If you don't have real order data (no backend
is connected in this demo), politely say you'd need to look it up in the real system,
but still guide the user on what happens next.
"""

app = Flask(__name__)

# Simple in-memory chat history per session id (demo only; use a DB for production)
sessions = {}

MENU = [
    {"id": 1, "name": "Margherita Pizza", "price": 249},
    {"id": 2, "name": "Paneer Tikka Wrap", "price": 149},
    {"id": 3, "name": "Veg Biryani", "price": 199},
    {"id": 4, "name": "Chicken Burger", "price": 179},
    {"id": 5, "name": "Cold Coffee", "price": 99},
]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/menu")
def menu():
    return jsonify(MENU)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    if session_id not in sessions:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_PROMPT,
        )
        sessions[session_id] = model.start_chat(history=[])

    chat_session = sessions[session_id]

    try:
        response = chat_session.send_message(user_message)
        reply = response.text
    except Exception as e:
        return jsonify({"error": f"Gemini API error: {str(e)}"}), 500

    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
