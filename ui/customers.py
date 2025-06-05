from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QInputDialog, QLabel, QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import sqlite3

class CustomersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titolo della pagina
        title_label = QLabel("Gestion des Clients")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E86C1; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Tabella clienti
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nom", "Téléphone", "Email", "Historique des ventes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Pulsanti
        button_layout = QHBoxLayout()

        self.add_customer_button = QPushButton("Ajouter un Client")
        self.add_customer_button.clicked.connect(self.add_customer)
        button_layout.addWidget(self.add_customer_button)

        self.modify_customer_button = QPushButton("Modifier/Supprimer un Client")
        self.modify_customer_button.clicked.connect(self.modify_or_delete_customer)
        button_layout.addWidget(self.modify_customer_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_data(self):
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT customer_name, phone, email FROM customers")
            rows = cursor.fetchall()
            connection.close()

            self.table.setRowCount(0)
            for row_data in rows:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Erreur Chargement", f"Erreur lors du chargement des clients : {str(e)}")

    def add_customer(self):
        name, ok = QInputDialog.getText(self, "Nouveau Client", "Nom du client:")
        if ok and name:
            phone, ok = QInputDialog.getText(self, "Nouveau Client", "Numéro de téléphone:")
            if ok:
                email, ok = QInputDialog.getText(self, "Nouveau Client", "Adresse e-mail:")
                if ok:
                    connection = sqlite3.connect("gestion_meca.db")
                    cursor = connection.cursor()
                    cursor.execute("INSERT INTO customers (customer_name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
                    connection.commit()
                    connection.close()
                    self.load_data()

    def modify_or_delete_customer(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un client à modifier ou supprimer.")
            return

        customer_name = self.table.item(selected_row, 0).text()
        action, ok = QInputDialog.getItem(self, "Options", "Sélectionnez une action:", ["Modifier", "Supprimer"], editable=False)
        if ok and action == "Modifier":
            self.modify_customer(customer_name)
        elif ok and action == "Supprimer":
            self.delete_customer(customer_name)

    def modify_customer(self, customer_name):
        phone, ok = QInputDialog.getText(self, "Modifier Client", "Nouveau numéro de téléphone:")
        if ok:
            email, ok = QInputDialog.getText(self, "Modifier Client", "Nouvelle adresse e-mail:")
            if ok:
                connection = sqlite3.connect("gestion_meca.db")
                cursor = connection.cursor()
                cursor.execute("UPDATE customers SET phone = ?, email = ? WHERE customer_name = ?", (phone, email, customer_name))
                connection.commit()
                connection.close()
                self.load_data()

    def delete_customer(self, customer_name):
        confirmation = QMessageBox.question(self, "Confirmation", f"Voulez-vous supprimer le client '{customer_name}'?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("DELETE FROM customers WHERE customer_name = ?", (customer_name,))
            connection.commit()
            connection.close()
            self.load_data()
