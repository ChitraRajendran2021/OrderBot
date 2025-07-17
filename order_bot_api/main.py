import re
from db import get_order_status, get_orders_by_date
from gemini import ask_gemini

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

def main():
    print("Welcome to OrderBot (Type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        order_id = detect_order_query(user_input)
        if order_id:
            status = get_order_status(order_id)
            print(f"OrderBot (from DB): Status of order {order_id} is: {status}")
            continue

        order_date = detect_date_query(user_input)
        if order_date:
            results = get_orders_by_date(order_date)
            if isinstance(results, str):
                print(f"OrderBot (from DB): {results}")
            else:
                print(f"Orders from {order_date}:")
                for row in results:
                    print(f"- Order ID: {row[0]}, Status: {row[1]}, Created: {row[2]}")
            continue

        response = ask_gemini(user_input)
        print(f"OrderBot (Gemini): {response}")

if __name__ == "__main__":
    main()
