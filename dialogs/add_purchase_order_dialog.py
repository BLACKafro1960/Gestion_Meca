from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialogButtonBox
from PySide6.QtGui import QFont
from PySide6.QtCore import QDate
from dialogs.add_item_row_dialog import AddItemRowDialog

class AddPurchaseOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvel Ordre d'Achat")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Form per i dettagli dell'ordine
        form_layout = QFormLayout()

        self.supplier_name_input = QLineEdit(placeholderText="Nom du fournisseur...")
        form_layout.addRow("Fournisseur:", self.supplier_name_input)

        self.order_date_input = QDateEdit(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)
        form_layout.addRow("Date de Commande:", self.order_date_input)

        self.delivery_date_input = QDateEdit(QDate.currentDate().addDays(7))
        self.delivery_date_input.setCalendarPopup(True)
        form_layout.addRow("Date de Livraison Prévue:", self.delivery_date_input)

        layout.addLayout(form_layout)

        # Lista per le righe dell'ordine
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Article", "Quantité", "Montant Total (CFA)"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.items_table)

        # Pulsante per aggiungere una riga
        add_item_button = QPushButton("Ajouter une ligne")
        add_item_button.clicked.connect(self.add_item_row)
        layout.addWidget(add_item_button)

        # Pulsanti OK e Annulla
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def add_item_row(self):
        """Aggiunge una nuova riga alla tabella delle righe dell'ordine."""
        dialog = AddItemRowDialog(self)
        if dialog.exec():  # Se l'utente conferma
            article_name, quantity, total_amount = dialog.get_data()

            # Verifica che i dati siano validi
            if not article_name or quantity < 1 or total_amount <= 0:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer des données valides.")
                return

            # Inserisci la nuova riga nella tabella
            row_number = self.items_table.rowCount()
            self.items_table.insertRow(row_number)
            self.items_table.setItem(row_number, 0, QTableWidgetItem(article_name))
            self.items_table.setItem(row_number, 1, QTableWidgetItem(str(quantity)))
            self.items_table.setItem(row_number, 2, QTableWidgetItem(f"{total_amount:.2f}"))

    def get_data(self):
        """Restituisce i dati dell'ordine."""
        supplier_name = self.supplier_name_input.text().strip()
        order_date = self.order_date_input.date().toString("dd-MM-yyyy")
        delivery_date = self.delivery_date_input.date().toString("dd-MM-yyyy")

        items = []
        for row in range(self.items_table.rowCount()):
            article_name = self.items_table.item(row, 0).text()
            quantity = int(self.items_table.item(row, 1).text())
            total_amount = float(self.items_table.item(row, 2).text())
            items.append((article_name, quantity, total_amount))

        return supplier_name, order_date, delivery_date, items
