import unittest
import sqlite3
from datetime import datetime
from unittest.mock import patch, MagicMock

# Assicurati che il percorso per importare config e database sia corretto
# Potrebbe essere necessario aggiungere il percorso del progetto a sys.path se i test sono in una sottocartella
import sys
import os

# Aggiungi la directory principale del progetto al percorso di Python
# Questo permette di importare i moduli come 'config' e 'database'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from config import DATABASE_PATH # Useremo un DB in memoria per i test
from database import (
    execute_query, fetch_all, fetch_one,
    add_article, get_all_articles, update_article, delete_article,
    add_sale, add_expense,
    add_customer, get_all_customers,
    add_supplier, get_all_suppliers,
    add_purchase_order, add_purchase_order_item
)

# Sovrascrivi DATABASE_PATH per i test per usare un database in memoria
TEST_DATABASE_PATH = ":memory:"

def initialize_test_database(connection):
    """Inizializza lo schema del database per i test."""
    cursor = connection.cursor()
    # Tabella Articoli
    cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_name TEXT NOT NULL,
        purchase_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        profit REAL NOT NULL
    )''')
    # Tabella Vendite
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_name TEXT NOT NULL,
        quantity_sold INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        sale_date TEXT NOT NULL,
        customer_name TEXT,
        payment_method TEXT
    )''')
    # Tabella Spese
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_type TEXT NOT NULL,
        amount REAL NOT NULL,
        expense_date TEXT NOT NULL
    )''')
    # Tabella Clienti
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT,
        email TEXT
    )''')
    # Tabella Fornitori
    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact_info TEXT
    )''')
    # Tabella Ordini di Acquisto
    cursor.execute('''CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        order_date TEXT NOT NULL,
        delivery_date TEXT,
        status TEXT NOT NULL
    )''')
    # Tabella Dettagli delle Righe degli Ordini di Acquisto
    cursor.execute('''CREATE TABLE IF NOT EXISTS purchase_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        article_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES purchase_orders(id)
    )''')
    connection.commit()

class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        """Configura un database in memoria per ogni test."""
        self.connection = sqlite3.connect(TEST_DATABASE_PATH)
        initialize_test_database(self.connection)
        # Patch DATABASE_PATH nel modulo 'database' per usare il DB di test
        self.db_path_patcher = patch('database.DATABASE_PATH', TEST_DATABASE_PATH)
        self.db_path_patcher.start()

    def tearDown(self):
        """Chiude la connessione al database e ferma il patcher."""
        self.db_path_patcher.stop()
        self.connection.close()

    def test_add_and_get_article(self):
        """Testa l'aggiunta e il recupero di un articolo."""
        article_id = add_article("Test Article 1", 10.0, 15.0, 100) # Profit = (15 - 10) * 100 = 500
        self.assertIsNotNone(article_id, "L'ID dell'articolo non dovrebbe essere None")

        articles = get_all_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0][1], "Test Article 1") # article_name
        self.assertEqual(articles[0][2], 10.0)        # purchase_price
        self.assertEqual(articles[0][3], 15.0)        # sale_price
        self.assertEqual(articles[0][4], 100)         # quantity
        self.assertEqual(articles[0][5], (15.0 - 10.0) * 100) # profit

    def test_update_article(self):
        """Testa l'aggiornamento di un articolo."""
        article_id = add_article("Old Name", 5.0, 8.0, 50)
        self.assertIsNotNone(article_id)

        update_result = update_article(article_id, "New Name", 6.0, 10.0, 60)
        self.assertIsNotNone(update_result, "L'aggiornamento dovrebbe avere successo")

        # Recupera l'articolo aggiornato direttamente per verifica
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE id=?", (article_id,))
        updated_article = cursor.fetchone()

        self.assertIsNotNone(updated_article)
        self.assertEqual(updated_article[1], "New Name")
        self.assertEqual(updated_article[2], 6.0)
        self.assertEqual(updated_article[3], 10.0)
        self.assertEqual(updated_article[4], 60)
        self.assertEqual(updated_article[5], (10.0 - 6.0) * 60)

    def test_delete_article(self):
        """Testa l'eliminazione di un articolo."""
        article_id1 = add_article("To Delete", 1.0, 2.0, 10)
        article_id2 = add_article("To Keep", 3.0, 4.0, 20)
        self.assertIsNotNone(article_id1)
        self.assertIsNotNone(article_id2)

        delete_result = delete_article(article_id1)
        self.assertIsNotNone(delete_result, "L'eliminazione dovrebbe avere successo")

        articles = get_all_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0][1], "To Keep")

        # Verifica che l'articolo sia stato effettivamente eliminato
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM articles WHERE id=?", (article_id1,))
        deleted_article = cursor.fetchone()
        self.assertIsNone(deleted_article)

    @patch('database.datetime') # Mock del modulo datetime all'interno di database.py
    def test_add_sale(self, mock_datetime):
        """Testa l'aggiunta di una vendita con data mockata."""
        # Configura il mock per restituire una data fissa
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_date

        # Prima aggiungi un articolo per la vendita
        add_article("Sale Item", 20.0, 30.0, 5) # Profit = (30 - 20) * 5 = 50

        sale_id = add_sale("Sale Item", 2, 60.0, "Test Customer", "Cash")
        self.assertIsNotNone(sale_id)

        # Verifica direttamente nel database
        cursor = self.connection.cursor()
        cursor.execute("SELECT article_name, quantity_sold, total_amount, sale_date, customer_name, payment_method FROM sales WHERE id = ?", (sale_id,))
        sale_data = cursor.fetchone()

        print(f"Sale data: {sale_data}") # DEBUG - Controlla cosa viene letto dal DB

        self.assertIsNotNone(sale_data)
        self.assertEqual(sale_data[0], "Sale Item")
        self.assertEqual(sale_data[1], 2)
        self.assertEqual(sale_data[2], 60.0)
        self.assertEqual(sale_data[3], fixed_date.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(sale_data[4], "Test Customer")
        self.assertEqual(sale_data[5], "Cash")
    # Aggiungi altri test per add_expense, add_customer, add_supplier, ecc.
    # Ricorda di creare le rispettive tabelle in initialize_test_database

if __name__ == '__main__':
    unittest.main()