import sqlite3
from datetime import datetime
import logging # Importa il modulo logging

# Configura un logger specifico per questo modulo se necessario, o usa il root logger
from config import DATABASE_PATH # Importa DATABASE_PATH

def execute_query(query, params=None):
    connection = sqlite3.connect(DATABASE_PATH) # Usa DATABASE_PATH
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Errore nell'esecuzione della query '{query[:50]}...': {e}")
        return None
    finally:
        connection.close()

def fetch_all(query, params=None):
    connection = sqlite3.connect(DATABASE_PATH) # Usa DATABASE_PATH
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Errore nel recupero dei dati con query '{query[:50]}...': {e}")
        return []
    finally:
        connection.close()

def fetch_one(query, params=None):
    connection = sqlite3.connect(DATABASE_PATH) # Usa DATABASE_PATH
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Errore nel recupero dei dati con query '{query[:50]}...': {e}")
        return None
    finally:
        connection.close()

# Funzioni per gli articoli
def add_article(article_name, purchase_price, sale_price, quantity):
    profit = (sale_price - purchase_price) * quantity
    query = "INSERT INTO articles (article_name, purchase_price, sale_price, quantity, profit) VALUES (?, ?, ?, ?, ?)"
    return execute_query(query, (article_name, purchase_price, sale_price, quantity, profit))

def update_article(article_id, article_name, purchase_price, sale_price, quantity):
    profit = (sale_price - purchase_price) * quantity
    query = "UPDATE articles SET article_name=?, purchase_price=?, sale_price=?, quantity=?, profit=? WHERE id=?"
    return execute_query(query, (article_name, purchase_price, sale_price, quantity, profit, article_id))

def delete_article(article_id):
    query = "DELETE FROM articles WHERE id=?"
    return execute_query(query, (article_id,))

def get_all_articles():
    return fetch_all("SELECT * FROM articles")

# Funzioni per le vendite
def add_sale(article_name, quantity_sold, total_amount, customer_name=None, payment_method=None):
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "INSERT INTO sales (article_name, quantity_sold, total_amount, sale_date, customer_name, payment_method) VALUES (?, ?, ?, ?, ?, ?)"
    return execute_query(query, (article_name, quantity_sold, total_amount, sale_date, customer_name, payment_method))

# Funzioni per le spese
def add_expense(expense_type, amount):
    expense_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "INSERT INTO expenses (expense_type, amount, expense_date) VALUES (?, ?, ?)"
    return execute_query(query, (expense_type, amount, expense_date))

# Funzioni per i clienti
def add_customer(customer_name, phone=None, email=None):
    query = "INSERT INTO customers (customer_name, phone, email) VALUES (?, ?, ?)"
    return execute_query(query, (customer_name, phone, email))

def get_all_customers():
    return fetch_all("SELECT * FROM customers")

# Funzioni per i fornitori
def add_supplier(supplier_name, contact_info):
    query = "INSERT INTO suppliers (supplier_name, contact_info) VALUES (?, ?)"
    return execute_query(query, (supplier_name, contact_info))

def get_all_suppliers():
    return fetch_all("SELECT * FROM suppliers")

# Funzioni per gli ordini di acquisto
def add_purchase_order(supplier_name, order_date, status, delivery_date=None):
    query = "INSERT INTO purchase_orders (supplier_name, order_date, delivery_date, status) VALUES (?, ?, ?, ?)"
    return execute_query(query, (supplier_name, order_date, delivery_date, status))

def add_purchase_order_item(order_id, article_name, quantity, total_amount):
    query = "INSERT INTO purchase_order_items (order_id, article_name, quantity, total_amount) VALUES (?, ?, ?, ?)"
    return execute_query(query, (order_id, article_name, quantity, total_amount))