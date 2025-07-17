from flask import Flask, request, jsonify
from flask_cors import CORS
import re

from db import get_order_status, get_orders_by_date
from gemini import ask_gemini

app = Flask(__name__)
CORS(app)  # Allow requests from frontend (localhost:5173)

def detect_order_query(text):
    if "order" in text.lower() and "status" in text.lower():
        match = re.search(r'\b(\d{5,})\b', text)
        if match:
            return int(match.group(1))
    return None

def detect_date_query(text):
    match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
    if "orders" in text.lower() and match:
        return match.group(1)
    return None

@app.route("/api/query", methods=["POST"])
def query():
    data = request.get_json()
    user_input = data.get("query", "")

    order_id = detect_order_query(user_input)
    if order_id:
        status = get_order_status(order_id)
        return jsonify({"response": f"Status of order {order_id} is: {status}"})

    order_date = detect_date_query(user_input)
    if order_date:
        results = get_orders_by_date(order_date)
        if isinstance(results, str):
            return jsonify({"response": results})
        else:
            formatted = "\n".join(
                f"- Order ID: {row[0]}, Status: {row[1]}, Created: {row[2]}" for row in results
            )
            return jsonify({"response": f"Orders from {order_date}:\n{formatted}"})

    # Fallback to Gemini
    response = ask_gemini(user_input)
    return jsonify({"response": f"{response}"})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
-------------------------------------------------
import logging
import time
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

from db import get_order_status, get_orders_by_date
from gemini import ask_gemini

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

app = Flask(__name__)
CORS(app)

# Detect order ID
def detect_order_query(text):
    match = re.search(r'\b(\d{5,})\b', text)
    if "order" in text.lower() and "status" in text.lower() and match:
        return int(match.group(1)), match.group(0)
    return None, None

# Detect order date
def detect_date_query(text):
    match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
    if "orders" in text.lower() and match:
        return match.group(1)
    return None

# Translate to English (safe for Gemini)
def translate_to_english(text):
    prompt = f"Translate the following message to English, preserving numbers and placeholders:\n\n{text}"
    return ask_gemini(prompt).strip()

# Translate back to original language
def translate_back(text, target_language_sample):
    prompt = (
        f"Translate the following response to the same language as this message:\n\n"
        f"Original Message: {target_language_sample}\n"
        f"Response: {text}"
    )
    return ask_gemini(prompt).strip()

@app.route("/api/query", methods=["POST"])
def query():
    start_time = time.time()
    try:
        data = request.get_json()
        user_input = data.get("query", "").strip()
        logging.info(f"Received query: {user_input}")

        # Step 1: Detect and sanitize
        order_id_match = re.search(r'\b(\d{5,})\b', user_input)
        order_date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', user_input)

        order_id_str = order_id_match.group(0) if order_id_match else None
        order_date_str = order_date_match.group(0) if order_date_match else None

        sanitized_input = user_input
        if order_id_str:
            sanitized_input = sanitized_input.replace(order_id_str, "{ORDER_ID}")
        if order_date_str:
            sanitized_input = sanitized_input.replace(order_date_str, "{ORDER_DATE}")

        logging.info(f"Sanitized user input: {sanitized_input}")

        # Step 2: Translate sanitized input to English
        translated_input = translate_to_english(sanitized_input)
        logging.info(f"Translated to English (sanitized): {translated_input}")

        # Step 3: Try local DB queries first (based on translated input)
        order_id, _ = detect_order_query(translated_input)
        if order_id:
            status = get_order_status(order_id)
            english_response = f"Status of order {order_id} is: {status}"
            final_response = translate_back(english_response, user_input)
            logging.info(f"DB Order Status Response: {final_response}")
            return jsonify({"response": final_response})

        order_date = detect_date_query(translated_input)
        if order_date:
            results = get_orders_by_date(order_date)
            if isinstance(results, str):  # Error message or no orders
                final_response = translate_back(results, user_input)
                logging.info(f"DB Date Query Response (Error): {final_response}")
                return jsonify({"response": final_response})
            else:
                orders = "\n".join(
                    f"- Order ID: {row[0]}, Status: {row[1]}, Created: {row[2]}" for row in results
                )
                english_response = f"Orders from {order_date}:\n{orders}"
                final_response = translate_back(english_response, user_input)
                logging.info(f"DB Date Query Response (List): {final_response}")
                return jsonify({"response": final_response})

        # Step 4: Fallback to Gemini (safe, sanitized, translated input)
        logging.info(f"Sending sanitized prompt to Gemini: {translated_input}")
        ai_response = ask_gemini(translated_input)

        # Step 5: Restore any placeholders if needed
        if '{ORDER_ID}' in translated_input and order_id_str:
            ai_response = ai_response.replace('{ORDER_ID}', order_id_str)
        if '{ORDER_DATE}' in translated_input and order_date_str:
            ai_response = ai_response.replace('{ORDER_DATE}', order_date_str)

        # Step 6: Translate back to original language
        final_response = translate_back(ai_response, user_input)
        logging.info(f"Gemini AI Fallback Response: {final_response}")
        return jsonify({"response": final_response})

    except Exception as e:
        logging.error(f"Error in query processing: {e}", exc_info=True)
        return jsonify({"response": "Sorry, something went wrong."}), 500

    finally:
        elapsed_time = time.time() - start_time
        logging.info(f"Query processed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
