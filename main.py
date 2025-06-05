import sys
import logging
from PySide6.QtWidgets import QApplication
import os

# Aggiungi la directory contenente main.py (che dovrebbe essere la radice del progetto
# rispetto alle cartelle 'ui' e 'utils') a sys.path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)
from ui.main_window import GestionMeca
import sqlite3
from config import DATABASE_PATH, ensure_directories # BACKUP_INTERVAL non è usato qui
from utils.backup_manager import BackupManager # Importa la classe BackupManager

# Configura il logging
logging.basicConfig(level=logging.DEBUG)

# Database setup - Definizione della funzione
def initialize_database():
    connection = sqlite3.connect(DATABASE_PATH) # Usa la costante DATABASE_PATH
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
    connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ensure_directories() # Assicura che le directory di configurazione esistano
    initialize_database()  # Chiama la funzione per inizializzare il DB

    # Esegui un backup all'avvio dell'applicazione
    logging.info("Eseguo backup all'avvio...")
    if not BackupManager.create_backup(): # Chiama il metodo statico della classe
        logging.error("Backup iniziale fallito.")
        # Qui potresti voler mostrare un QMessageBox all'utente se il backup iniziale fallisce

    window = GestionMeca()
    window.show()
    sys.exit(app.exec())
