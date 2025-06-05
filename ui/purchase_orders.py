from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDialog, QFormLayout, QLineEdit, QDateEdit, QListWidget, QListWidgetItem, QLabel, QInputDialog
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDate
import sqlite3
from datetime import datetime
from dialogs.add_purchase_order_dialog import AddPurchaseOrderDialog
from dialogs.order_details_dialog import OrderDetailsDialog

class PurchaseOrdersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Tabella principale per gli ordini di acquisto
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Ordine", "Fornitore", "Data Ordine", "Data Consegna", "Stato"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)      
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                margin: 10px 0;
            }
            QHeaderView::section {
                background-color: #2E86C1;
                color: white;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
                color: black;
            }
        """)
        self.table.cellDoubleClicked.connect(self.show_order_details)
        layout.addWidget(self.table)

        # Pulsanti per aggiungere/modificare/eliminare ordini
        button_layout = QHBoxLayout()
        self.add_order_button = QPushButton("Ajouter un Ordre")
        self.add_order_button.clicked.connect(self.add_purchase_order)
        button_layout.addWidget(self.add_order_button)

        self.modify_order_button = QPushButton("Modifier/Supprimer un Ordre")
        self.modify_order_button.clicked.connect(self.modify_or_delete_order)
        button_layout.addWidget(self.modify_order_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Carica i dati dalla tabella degli ordini
        self.load_data()

    def load_data(self):
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT id, supplier_name, order_date, delivery_date, status FROM purchase_orders")
            rows = cursor.fetchall()
            connection.close()

            self.table.setRowCount(0)  # Resetta la tabella
            for row_data in rows:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)

                # Aggiungi i dati alle colonne
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_number, column_number, item)

                # Colori condizionali per lo stato
                if row_data[4] == "Terminé":
                    self.table.item(row_number, 4).setBackground(Qt.green)
                elif row_data[4] == "En attente":
                    self.table.item(row_number, 4).setBackground(Qt.yellow)
                elif row_data[4] == "Retardé":
                    self.table.item(row_number, 4).setBackground(Qt.red)

        except Exception as e:
            QMessageBox.critical(self, "Erreur Chargement", f"Erreur lors du chargement des ordres : {str(e)}")

    def show_order_details(self, row, column):
        """Mostra i dettagli dell'ordine selezionato."""
        order_id = self.table.item(row, 0).text()

        # Recupera i dettagli dall'ordine
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()

            # Recupera le righe dell'ordine
            cursor.execute("SELECT article_name, quantity, total_amount FROM purchase_order_items WHERE order_id = ?", (order_id,))
            items = cursor.fetchall()

            # Recupera i dettagli generali dell'ordine
            cursor.execute("SELECT supplier_name, order_date, delivery_date, status FROM purchase_orders WHERE id = ?", (order_id,))
            order_details = cursor.fetchone()

            connection.close()

            # Mostra la finestra dettagliata
            if order_details and items:
                dialog = OrderDetailsDialog(order_id, order_details, items)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Avertissement", "Aucune donnée disponible pour cet ordre.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du récupéro des détails de l'ordre : {str(e)}")

    def add_purchase_order(self):
        """Crea un nuovo ordine di acquisto."""
        dialog = AddPurchaseOrderDialog(self)
        if dialog.exec():
            supplier_name, order_date, delivery_date, items = dialog.get_data()

            try:
                connection = sqlite3.connect("gestion_meca.db")
                cursor = connection.cursor()

                # Inserisci l'ordine principale
                cursor.execute(
                    "INSERT INTO purchase_orders (supplier_name, order_date, delivery_date, status) VALUES (?, ?, ?, ?)",
                    (supplier_name, order_date, delivery_date, "In Attesa"),
                )
                order_id = cursor.lastrowid  # Ottieni l'ID dell'ordine appena creato

                # Inserisci le righe associate
                for item in items:
                    article_name, quantity, total_amount = item
                    cursor.execute(
                        "INSERT INTO purchase_order_items (order_id, article_name, quantity, total_amount) VALUES (?, ?, ?, ?)",
                        (order_id, article_name, quantity, total_amount),
                    )

                connection.commit()
                connection.close()

                self.load_data()  # Aggiorna la tabella degli ordini
                QMessageBox.information(self, "Succès", "L'ordre d'achat a été créé avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la création de l'ordre : {str(e)}")

    def modify_or_delete_order(self):
        """Modifica o elimina un ordine."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un ordre à modifier ou supprimer.")
            return

        order_id = self.table.item(selected_row, 0).text()
        action, ok = QInputDialog.getItem(self, "Options", "Sélectionnez une action:", ["Modifier", "Supprimer"], editable=False)
        if not ok:
            return

        if action == "Modifier":
            self.modify_order(order_id)
        elif action == "Supprimer":
            self.delete_order(order_id)

    def modify_order(self, order_id):
        """Modifica un ordine esistente."""
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()

            # Recupera i dettagli attuali
            cursor.execute("SELECT supplier_name, delivery_date, status FROM purchase_orders WHERE id = ?", (order_id,))
            current_details = cursor.fetchone()

            supplier_name, ok = QInputDialog.getText(self, "Modifier Ordre", "Nom du fournisseur:", text=current_details[0])
            if not ok:
                return

            delivery_date, ok = QInputDialog.getText(self, "Modifier Ordre", "Date de livraison prévue (jj-mm-aaaa):", text=current_details[1] or "")
            if not ok:
                return

            status, ok = QInputDialog.getItem(self, "Modifier Ordre", "Statut:", ["En attente", "Terminé", "Retardé"], editable=False)
            if not ok:
                return

            cursor.execute(
                "UPDATE purchase_orders SET supplier_name = ?, delivery_date = ?, status = ? WHERE id = ?",
                (supplier_name, delivery_date, status, order_id),
            )
            connection.commit()
            connection.close()
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification de l'ordre : {str(e)}")

    def delete_order(self, order_id):
        """Elimina un ordine."""
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous supprimer cet ordre ({order_id}) ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            try:
                connection = sqlite3.connect("gestion_meca.db")
                cursor = connection.cursor()
                cursor.execute("DELETE FROM purchase_orders WHERE id = ?", (order_id,))
                cursor.execute("DELETE FROM purchase_order_items WHERE order_id = ?", (order_id,))
                connection.commit()
                connection.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression de l'ordre : {str(e)}")
