from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QGridLayout, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import sqlite3
from datetime import datetime, timedelta
import pyqtgraph as pg

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Statistiche
        stats_layout = QGridLayout()

        # Totale vendite
        total_sales_frame = QFrame()
        total_sales_frame.setStyleSheet("background-color: #2E86C1; color: white; border-radius: 10px; padding: 15px;")
        total_sales_layout = QVBoxLayout()
        total_sales_layout.addWidget(QLabel("Total des Ventes"))
        self.total_sales_label = QLabel("0 CFA")
        total_sales_layout.addWidget(self.total_sales_label)
        total_sales_frame.setLayout(total_sales_layout)
        stats_layout.addWidget(total_sales_frame, 0, 0)

        # Totale spese
        total_expenses_frame = QFrame()
        total_expenses_frame.setStyleSheet("background-color: #FFA07A; color: white; border-radius: 10px; padding: 15px;")
        total_expenses_layout = QVBoxLayout()
        total_expenses_layout.addWidget(QLabel("Total des Dépenses"))
        self.total_expenses_label = QLabel("0 CFA")
        total_expenses_layout.addWidget(self.total_expenses_label)
        total_expenses_frame.setLayout(total_expenses_layout)
        stats_layout.addWidget(total_expenses_frame, 0, 1)

        # Stock basso
        low_stock_frame = QFrame()
        low_stock_frame.setStyleSheet("background-color: #FFD700; color: black; border-radius: 10px; padding: 15px;")
        low_stock_layout = QVBoxLayout()
        low_stock_layout.addWidget(QLabel("Stock Bas (<5)"))
        self.low_stock_label = QLabel("0 Articles")
        low_stock_layout.addWidget(self.low_stock_label)
        low_stock_frame.setLayout(low_stock_layout)
        stats_layout.addWidget(low_stock_frame, 1, 0)

        # Cliente più attivo
        top_customer_frame = QFrame()
        top_customer_frame.setStyleSheet("background-color: #90EE90; color: black; border-radius: 10px; padding: 15px;")
        top_customer_layout = QVBoxLayout()
        top_customer_layout.addWidget(QLabel("Client Plus Actif"))
        self.top_customer_label = QLabel("Nessuno")
        top_customer_layout.addWidget(self.top_customer_label)
        top_customer_frame.setLayout(top_customer_layout)
        stats_layout.addWidget(top_customer_frame, 1, 1)

        layout.addLayout(stats_layout)

        # Grafico vendite
        try:
            if pg is not None:
                self.sales_graph = pg.PlotWidget()
                self.sales_graph.setTitle("Ventes des Derniers 30 Jours")
                self.sales_graph.setLabel('left', 'Montant (CFA)')
                self.sales_graph.setLabel('bottom', 'Jours')
                layout.addWidget(self.sales_graph)
            else:
                no_graph_label = QLabel("Le graphique ne peut pas être affiché car pyqtgraph n'est pas installé.")
                no_graph_label.setStyleSheet("color: red; font-size: 14px;")
                layout.addWidget(no_graph_label)
        except Exception as e:
            QMessageBox.critical(self, "Erreur PyQtGraph", f"Erreur lors de l'initialisation du graphique : {str(e)}")

        self.setLayout(layout)

    def update_dashboard(self):
        try:
            with sqlite3.connect("gestion_meca.db") as connection:
                cursor = connection.cursor()

                # Totale vendite
                cursor.execute("SELECT SUM(total_amount) FROM sales")
                total_sales = cursor.fetchone()[0] or 0

                # Totale spese
                cursor.execute("SELECT SUM(amount) FROM expenses")
                total_expenses = cursor.fetchone()[0] or 0

                # Stock basso
                cursor.execute("SELECT COUNT(*) FROM articles WHERE quantity < 5")
                low_stock_count = cursor.fetchone()[0]

                # Cliente più attivo
                cursor.execute("""
                    SELECT customer_name, SUM(total_amount)
                    FROM sales
                    GROUP BY customer_name
                    ORDER BY SUM(total_amount) DESC
                    LIMIT 1
                """)
                top_customer = cursor.fetchone()

                # Aggiorna i valori nel dashboard
                self.total_sales_label.setText(f"{total_sales:.2f} CFA")
                self.total_expenses_label.setText(f"{total_expenses:.2f} CFA")
                self.low_stock_label.setText(f"{low_stock_count} Articles")
                self.top_customer_label.setText(top_customer[0] if top_customer else "Nessuno")

                # Aggiorna il grafico delle vendite
                if hasattr(self, 'sales_graph') and pg is not None:
                    today = datetime.now()
                    sales_data = []
                    with sqlite3.connect("gestion_meca.db") as connection:
                        cursor = connection.cursor()
                        for i in range(30):  # Prendi i dati degli ultimi 30 giorni
                            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                            cursor.execute("SELECT SUM(total_amount) FROM sales WHERE sale_date LIKE ?", (f"{date}%",))
                            amount = cursor.fetchone()[0] or 0
                            sales_data.append((i, amount))

                    x, y = zip(*sales_data)
                    self.sales_graph.clear()
                    self.sales_graph.plot(x, y, pen=pg.mkPen(color=(0, 128, 255), width=2))
        except Exception as e:
            QMessageBox.critical(self, "Erreur Mise à Jour", f"Erreur lors de la mise à jour du tableau de bord : {str(e)}")
