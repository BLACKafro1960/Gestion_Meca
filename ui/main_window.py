import sys
import logging
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QInputDialog, QLineEdit,
    QMessageBox, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer, QUrl # Importa QUrl
from PySide6.QtGui import QDesktopServices # Importa QDesktopServices
from ui.dashboard import DashboardPage
from ui.inventory import InventoryPage
from ui.sales import SalesPage
from ui.customers import CustomersPage
from ui.reports import ReportsPage
from ui.expenses import ExpensesPage
from ui.suppliers import SuppliersPage
from ui.purchase_orders import PurchaseOrdersPage
from database import fetch_all # Rimosso initialize_database dall'import
from config import BACKUP_INTERVAL # Importa BACKUP_INTERVAL
from utils.backup_manager import BackupManager
class GestionMeca(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestionMeca - Gestion des Pièces Mécaniques")
        # Imposta le dimensioni minime e massime della finestra
        # Imposta solo la dimensione minima per garantire una visualizzazione corretta
        self.setMinimumSize(870, 600)
        # Imposta la dimensione iniziale della finestra
        self.resize(1280, 720)
        # Abilita il ridimensionamento dinamico
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.password = "admin"  # Password predefinita per le modifiche
        self.setup_ui()
        self.load_data()
        self.connect_signals() # Connetti i segnali dopo aver creato i widget

        # Timer per il controllo dello stock basso
        self.stock_check_timer = QTimer(self) # Rimuovi il parent self qui, non necessario
        self.stock_check_timer.timeout.connect(self.check_low_stock)
        self.stock_check_timer.start(5 * 60 * 1000)  # Controlla ogni 5 minuti

    def setup_ui(self):
        # Layout principale
        self.layout = QVBoxLayout()

        # Titolo principale
        self.title_label = QLabel("GestionMeca - Gestion des Pièces Mécaniques")
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #2E86C1; margin-bottom: 20px;")
        self.layout.addWidget(self.title_label)

        # Widget Tab
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
        QTabBar::tab {
            padding: 10px;
            background-color: #f0f0f0;  /* Colore non selezionato */
            color: black;
            border: 1px solid #ccc;
            border-bottom-color: transparent;
        }
        QTabBar::tab:selected {
            background-color: #2E86C1;  /* Colore blu quando selezionata */
            color: white;
            border: 1px solid #000;
            border-bottom-color: transparent;
        }
        QTabBar::tab:hover {
            background-color: #a0c4ff;  /* Opzionale: effetto hover */
        }
        QTabWidget::pane {
            border-top: 1px solid #ccc;
        }
        """)

        # Aggiungi le schede
        self.dashboard_tab = DashboardPage()
        self.inventory_tab = InventoryPage(self)  # Passa self come parent
        self.sales_tab = SalesPage(self)
        self.customers_tab = CustomersPage() # Non sembra aver bisogno del parent per ora
        self.reports_tab = ReportsPage()
        self.expenses_tab = ExpensesPage(self)
        self.suppliers_tab = SuppliersPage(self)
        self.purchase_orders_tab = PurchaseOrdersPage()

        self.tabs.addTab(self.dashboard_tab, "Tableau de Bord")
        self.tabs.addTab(self.inventory_tab, "Inventaire")
        self.tabs.addTab(self.sales_tab, "Ventes")
        self.tabs.addTab(self.customers_tab, "Clients")
        self.tabs.addTab(self.reports_tab, "Rapports & Sauvegardes") # Rinomina la scheda
        self.tabs.addTab(self.expenses_tab, "Dépenses")
        self.tabs.addTab(self.suppliers_tab, "Fournisseurs")
        self.tabs.addTab(self.purchase_orders_tab, "Ordres d'Achat")

        self.layout.addWidget(self.tabs)

        # Contenitore principale
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #F9F9F9; padding: 20px;")
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Imposta la finestra come ridimensionabile
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def connect_signals(self):
        """Connette i segnali necessari."""
        # Passa il riferimento della main window alle pagine che ne hanno bisogno
        self.inventory_tab.parent_window = self
        self.sales_tab.main_window = self
        self.expenses_tab.parent_window = self
        self.suppliers_tab.parent_window = self
        self.reports_tab.parent_window = self # Passa il riferimento alla ReportsPage

    def load_data(self):
        try:
            # Il database viene già inizializzato in main.py
            
            # Carica i dati in modo sicuro con gestione degli errori
            tabs_to_load = [
                (self.inventory_tab, "Inventario"),
                (self.sales_tab, "Vendite"),
                (self.customers_tab, "Clienti"),
                (self.suppliers_tab, "Fornitori"),
                (self.purchase_orders_tab, "Ordini d'acquisto")
            ]
            
            for tab, name in tabs_to_load:
                try:
                    if hasattr(tab, 'load_data'):
                        tab.load_data()
                except Exception as tab_error:
                    # Usa logging.error per gli errori di caricamento dati specifici delle tab
                    logging.error(f"Errore nel caricamento dei dati di {name}: {tab_error}", exc_info=True)
                    QMessageBox.warning(self, "Attenzione", 
                        f"Errore nel caricamento dei dati di {name}. Alcune funzionalità potrebbero essere limitate.")
            
            # Aggiorna la dashboard dopo aver caricato tutti i dati
            try:
                if hasattr(self.dashboard_tab, 'update_dashboard'):
                    self.dashboard_tab.update_dashboard()
                # Avvia il timer per i backup automatici dopo che tutto è caricato
                self.start_backup_timer()
            except Exception as dash_error:
                # Usa logging.error per gli errori di aggiornamento dashboard
                logging.error(f"Errore nell'aggiornamento della dashboard: {dash_error}", exc_info=True)
                
        except Exception as e:
            # Usa logging.critical per errori gravi all'avvio
            logging.critical(f"Errore critico durante il caricamento dei dati: {str(e)}")
            QMessageBox.critical(self, "Errore Critico", 
                "Si è verificato un errore critico durante il caricamento dei dati.\n" +
                "Verificare la connessione al database e riprovare.")

    def request_password(self):
        try:
            password, ok = QInputDialog.getText(self, "Authentification", "Entrez le mot de passe pour continuer :", QLineEdit.Password)
            if not hasattr(self, 'password'):
                raise AttributeError("La variable 'password' n'est pas définie dans la classe GestionMeca.")
            if ok and password == self.password:
                self.inventory_tab.add_item()
            elif ok:
                QMessageBox.warning(self, "Erreur", "Mot de passe incorrect !")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Critique", f"Une erreur est survenue : {str(e)}")

    def start_backup_timer(self):
        """Avvia il timer per i backup automatici."""
        self.backup_timer = QTimer(self)
        # Converti BACKUP_INTERVAL da secondi a millisecondi
        self.backup_timer.timeout.connect(create_backup)
        self.backup_timer.start(BACKUP_INTERVAL * 1000)
        logging.info(f"Timer backup automatico avviato. Intervallo: {BACKUP_INTERVAL} secondi.")
    def check_low_stock(self):
        try:
            low_stock_items = fetch_all("SELECT article_name, quantity FROM articles WHERE quantity < 5")
            if low_stock_items:
                message = "Les articles suivants ont un stock bas (<5) :\n\n"
                for item in low_stock_items:
                    message += f"- {item[0]} : {item[1]} unités\n"
                QMessageBox.warning(self, "Stock Bas", message)
        except Exception as e:
            print(f"Erreur lors du contrôle du stock : {str(e)}")

    def update_dashboard(self):
        if hasattr(self, 'dashboard_tab'):
            self.dashboard_tab.update_dashboard()