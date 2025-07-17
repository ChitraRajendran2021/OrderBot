import logging
import time
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

import langid
from db import get_order_status, get_orders_by_date
from gemini import ask_gemini

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

app = Flask(__name__)
CORS(app)

# Language detection
def is_english(text):
    lang, _ = langid.classify(text)
    return lang == 'en'

# Detect order ID from text
def detect_order_query(text):
    match = re.search(r'\b(\d{5,})\b', text)
    if "order" in text.lower() and "status" in text.lower() and match:
        return int(match.group(1)), match.group(0)
    return None, None

# Detect order date from text
def detect_date_query(text):
    match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
    if "orders" in text.lower() and match:
        return match.group(1)
    return None

# Translate to English
def translate_to_english(text):
    prompt = f"Translate the following message to English, preserving numbers/dates:\n\n{text}"
    return ask_gemini(prompt).strip()

# Translate back to original language
def translate_back(text, target_language_sample):
    # Detect language of the original user message
    lang, _ = langid.classify(target_language_sample)
    
    # If original message is in English, skip translation
    if lang == 'en':
        return text

    # Otherwise, translate back to original language
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

        if is_english(user_input):
            translated_input = user_input
        else:
            translated_input = translate_to_english(user_input)
        logging.info(f"Translated to English: {translated_input}")

        # Check for order ID
        order_id, order_id_str = detect_order_query(translated_input)
        if order_id:
            status = get_order_status(order_id)
            english_response = f"Status of order {order_id} is: {status}"
            final_response = translate_back(english_response, user_input)
            logging.info(f"DB Order Status Response: {final_response}")
            return jsonify({"response": final_response})

        # Check for order date
        order_date = detect_date_query(translated_input)
        if order_date:
            results = get_orders_by_date(order_date)
            if isinstance(results, str):  # If results is a string (error message or no orders)
                final_response = translate_back(results, user_input)
                logging.info(f"DB Date Query Response (Error or No Orders): {final_response}")
                return jsonify({"response": final_response})
            else:  # If results is a list of orders
                orders = "\n".join(
                    f"- Order ID: {row[0]}, Status: {row[1]}, Created: {row[2]}" for row in results
                )
                english_response = f"Orders from {order_date}:\n{orders}"
                final_response = translate_back(english_response, user_input)
                logging.info(f"DB Date Query Response (List): {final_response}")
                return jsonify({"response": final_response})

        # If no valid order query, sanitize and send to Gemini AI
        sanitized_prompt = translated_input
        sanitized_prompt = re.sub(r'\b(\d{5,})\b', '{ORDER_ID}', sanitized_prompt)
        sanitized_prompt = re.sub(r'\b(\d{4}-\d{2}-\d{2})\b', '{ORDER_DATE}', sanitized_prompt)

        logging.info(f"Sanitized Gemini prompt: {sanitized_prompt}")

        # Fallback to Gemini
        ai_response = ask_gemini(sanitized_prompt)

        # Replace placeholders back if they existed
        if '{ORDER_ID}' in sanitized_prompt and order_id_str:
            ai_response = ai_response.replace('{ORDER_ID}', order_id_str)
        if '{ORDER_DATE}' in sanitized_prompt and order_date:
            ai_response = ai_response.replace('{ORDER_DATE}', order_date)

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
