from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QInputDialog, QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDate
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from dialogs.add_item_dialog import AddItemDialog
from dialogs.modify_item_dialog import ModifyItemDialog

class InventoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        # Layout principale
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Barra di ricerca
        self.search_input = QLineEdit(placeholderText="Rechercher un article...")
        self.search_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        self.search_input.textChanged.connect(self.filter_inventory)
        layout.addWidget(self.search_input)

        # Tabella inventario
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Aggiungi una colonna per il totale
        self.table.setHorizontalHeaderLabels([
            "Article", "Prix d'Achat (CFA)", "Prix de Vente (CFA)", "Quantité", "Bénéfice (CFA)", "Total (CFA)"
        ])

        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #3498DB;  /* Blu più chiaro */
                color: white;
                font-weight: bold;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                margin: 10px 0;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
            }
        """)

        layout.addWidget(self.table)

        # Pulsanti
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.setSpacing(10)

        button_style = """
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B4F72;
            }
        """

        self.report_button = QPushButton("Générer un Rapport")
        self.report_button.setStyleSheet(button_style)
        self.report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(self.report_button)

        self.add_item_button = QPushButton("Ajouter un Article")
        self.add_item_button.setStyleSheet(button_style)
        self.add_item_button.clicked.connect(self.request_password_for_add_item)
        button_layout.addWidget(self.add_item_button)

        self.modify_item_button = QPushButton("Modifier / Supprimer un Article")
        self.modify_item_button.setStyleSheet(button_style)
        self.modify_item_button.clicked.connect(self.request_password_for_modifications)
        button_layout.addWidget(self.modify_item_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_data(self):
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT article_name, purchase_price, sale_price, quantity, profit FROM articles")
            rows = cursor.fetchall()
            connection.close()

            self.table.setRowCount(0)
            for row_data in rows:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)
                total = row_data[2] * row_data[3]
                for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
                self.table.setItem(row_number, 5, QTableWidgetItem(f"{total:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Erreur Chargement", f"Erreur lors du chargement des données : {str(e)}")

    def filter_inventory(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in [0, 1, 2, 3]:  # Search in Article Name, Purchase Price, Sale Price, Quantity
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def generate_report(self):
        connection = sqlite3.connect("gestion_meca.db")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(quantity * sale_price), SUM(profit), COUNT(*), SUM(CASE WHEN quantity < 5 THEN 1 ELSE 0 END)
            FROM articles
        """)
        total_value, total_profit, total_articles, low_stock_count = cursor.fetchone()
        total_value = total_value or 0
        total_profit = total_profit or 0
        total_articles = total_articles or 0
        low_stock_count = low_stock_count or 0

        cursor.execute("SELECT article_name, quantity FROM articles WHERE quantity < 5")
        low_stock_items = cursor.fetchall()
        connection.close()

        # Generate PDF
        pdf_file_name = f"rapport_total_{datetime.now().strftime('%d-%m-%Y')}.pdf"
        pdf = SimpleDocTemplate(pdf_file_name, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph(f"<b>Rapport Total</b><br/><i>{datetime.now().strftime('%d/%m/%Y')}</i>", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Summary
        summary_data = [
            ["Valeur totale du stock", f"{total_value:.2f} CFA"],
            ["Bénéfice total", f"{total_profit:.2f} CFA"],
            ["Nombre total d'articles", f"{total_articles}"],
            ["Articles avec stock faible (< 5)", f"{low_stock_count}"],
        ]
        table = Table(summary_data, colWidths=[250, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        if low_stock_items:
            elements.append(Spacer(1, 24))
            elements.append(Paragraph("<b>Articles avec stock faible :</b>", styles["Heading2"]))
            low_stock_table_data = [["Nom de l'article", "Quantité"]] + low_stock_items
            low_stock_table = Table(low_stock_table_data, colWidths=[250, 150])
            low_stock_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(low_stock_table)

        pdf.build(elements)
        QMessageBox.information(self, "Succès", f"Le rapport a été exporté en PDF : {pdf_file_name}")

    def request_password_for_modifications(self):
        password, ok = QInputDialog.getText(self, "Authentification", "Entrez le mot de passe pour continuer :", QLineEdit.Password)
        if ok and password == self.parent_window.password:
            self.modify_or_delete_item()
        elif ok:
            QMessageBox.warning(self, "Erreur", "Mot de passe incorrect !")

    def request_password_for_add_item(self):
        password, ok = QInputDialog.getText(self, "Authentification", "Entrez le mot de passe pour continuer :", QLineEdit.Password)
        if ok and password == self.parent_window.password:
            self.add_item()
        elif ok:
            QMessageBox.warning(self, "Erreur", "Mot de passe incorrect !")

    def add_item(self):
        dialog = AddItemDialog()
        if dialog.exec():
            article_name, purchase_price, sale_price, quantity = dialog.get_data()

            # Controlla se l'articolo esiste già
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT quantity FROM articles WHERE article_name = ?", (article_name,))
            existing_record = cursor.fetchone()

            if existing_record:
                # L'articolo esiste già, aggiorna la quantità
                current_quantity = existing_record[0]
                new_quantity = current_quantity + quantity
                profit = (sale_price - purchase_price) * new_quantity
                cursor.execute(
                    "UPDATE articles SET quantity = ?, profit = ? WHERE article_name = ?",
                    (new_quantity, profit, article_name),
                )
                QMessageBox.information(self, "Succès", f"Quantité mise à jour pour l'article '{article_name}'.")
            else:
                # L'articolo non esiste, inserisci un nuovo record
                profit = (sale_price - purchase_price) * quantity
                cursor.execute(
                    "INSERT INTO articles (article_name, purchase_price, sale_price, quantity, profit) VALUES (?, ?, ?, ?, ?)",
                    (article_name, purchase_price, sale_price, quantity, profit),
                )
                QMessageBox.information(self, "Succès", f"L'article '{article_name}' a été ajouté avec succès.")

            connection.commit()
            connection.close()
            self.load_data()

    def modify_or_delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à modifier ou supprimer.")
            return

        article_name = self.table.item(selected_row, 0).text()
        dialog = ModifyItemDialog(article_name)
        if dialog.exec():
            action, data = dialog.get_data()
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            if action == "modify":
                purchase_price, sale_price, quantity = data
                profit = (sale_price - purchase_price) * quantity
                cursor.execute("UPDATE articles SET purchase_price = ?, sale_price = ?, quantity = ?, profit = ? WHERE article_name = ?",
                               (purchase_price, sale_price, quantity, profit, article_name))
            elif action == "delete":
                cursor.execute("DELETE FROM articles WHERE article_name = ?", (article_name,))
            connection.commit()
            connection.close()
            self.load_data()
