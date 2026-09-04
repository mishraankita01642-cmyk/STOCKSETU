from database import get_connection


def search_product(search_text):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT product_id, name, sku, category
        FROM products
        WHERE name LIKE ? OR sku LIKE ?
    """

    search_value = f"%{search_text}%"

    cursor.execute(query, (search_value, search_value))

    products = cursor.fetchall()

    conn.close()

    return products


def get_product_locations(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            locations.warehouse_code,
            locations.row_code,
            locations.bin_code,
            inventory.quantity
        FROM inventory
        JOIN locations
            ON inventory.location_id = locations.location_id
        WHERE inventory.product_id = ?
    """

    cursor.execute(query, (product_id,))

    locations = cursor.fetchall()

    conn.close()

    return locations


def get_total_stock(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT SUM(quantity)
        FROM inventory
        WHERE product_id = ?
    """

    cursor.execute(query, (product_id,))

    result = cursor.fetchone()

    conn.close()

    return result[0] if result[0] is not None else 0


def check_low_stock(product_id, threshold=5):
    total_stock = get_total_stock(product_id)

    return total_stock <= threshold