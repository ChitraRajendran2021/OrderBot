import mysql.connector
from config import DB_CONFIG

def get_order_status(order_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM oe_order WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else "Order not found."
    except Exception as e:
        return f"Database error: {e}"

def get_orders_by_date(date_str):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
            SELECT order_id, status, create_date 
            FROM oe_order 
            WHERE DATE(create_date) = %s
        """
        cursor.execute(query, (date_str,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results if results else "No orders found for that date."
    except Exception as e:
        return f"Database error: {e}"
