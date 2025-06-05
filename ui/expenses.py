from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QHeaderView, QInputDialog, QLineEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import sqlite3
from dialogs.add_expense_dialog import AddExpenseDialog
from dialogs.modify_expense_dialog import ModifyExpenseDialog

class ExpensesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Salva il riferimento alla finestra principale
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titolo della pagina
        title_label = QLabel("Gestion des Dépenses")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E86C1; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Tabella per visualizzare le spese
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Manteniamo solo 3 colonne (rimuoviamo "Actions")
        self.table.setHorizontalHeaderLabels(["Type de Dépense", "Montant (CFA)", "Date"])  # Nomi delle colonne in francese
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
        layout.addWidget(self.table)

        # Pulsanti per aggiungere/modificare/eliminare spese
        button_layout = QHBoxLayout()

        # Pulsante "Ajouter une Dépense"
        self.add_expense_button = QPushButton("Ajouter une Dépense")
        self.add_expense_button.setStyleSheet("""
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B4F72;
            }
        """)
        self.add_expense_button.clicked.connect(self.add_expense)
        button_layout.addWidget(self.add_expense_button)

        # Pulsante "Modifier / Supprimer une Dépense"
        self.modify_expense_button = QPushButton("Modifier / Supprimer une Dépense")
        self.modify_expense_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA07A;
                color: black;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
        """)
        self.modify_expense_button.clicked.connect(self.modify_or_delete_expense)
        button_layout.addWidget(self.modify_expense_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Carica i dati dalla tabella delle spese
        self.load_data()

    def load_data(self):
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT expense_type, amount, expense_date FROM expenses")
            rows = cursor.fetchall()
            connection.close()

            self.table.setRowCount(0)  # Resetta la tabella
            for row_data in rows:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)

                # Aggiungi i dati alle colonne
                for column_number, data in enumerate(row_data):
                    if isinstance(data, float):  # Formatta i numeri decimali
                        formatted_data = f"{data:.2f}"
                    else:
                        formatted_data = str(data)
                    item = QTableWidgetItem(formatted_data)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_number, column_number, item)

        except Exception as e:
            QMessageBox.critical(self, "Erreur Chargement", f"Erreur lors du chargement des données : {str(e)}")

    def add_expense(self):
        dialog = AddExpenseDialog(self)
        if dialog.exec():
            expense_type, amount, expense_date = dialog.get_data()
            if expense_type and amount is not None:
                try:
                    connection = sqlite3.connect("gestion_meca.db")
                    cursor = connection.cursor()
                    cursor.execute(
                        "INSERT INTO expenses (expense_type, amount, expense_date) VALUES (?, ?, ?)",
                        (expense_type, amount, expense_date),
                    )
                    connection.commit()
                    connection.close()
                    self.load_data()  # Aggiorna la tabella dopo l'inserimento
                    QMessageBox.information(self, "Succès", "La dépense a été enregistrée avec succès.")
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout de la dépense : {str(e)}")

    def modify_or_delete_expense(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une dépense à modifier ou supprimer.")
            return

        expense_type = self.table.item(selected_row, 0).text()
        amount = float(self.table.item(selected_row, 1).text())
        expense_date = self.table.item(selected_row, 2).text()

        # Chiedi all'utente se vuole modificare o eliminare
        action, ok = QInputDialog.getItem(
            self,
            "Options",
            "Sélectionnez une action:",
            ["Modifier", "Supprimer"],
            editable=False,
        )
        if not ok:
            return

        # Verifica la password prima di procedere
        if not self.request_password():
            return

        if action == "Modifier":
            self.modify_expense(selected_row)
        elif action == "Supprimer":
            self.delete_expense(selected_row)

    def request_password(self):
        """Richiede la password per le modifiche."""
        if not hasattr(self, 'parent_window') or not hasattr(self.parent_window, 'password'):
            QMessageBox.critical(self, "Erreur", "La variable 'password' n'est pas définie dans la classe principale.")
            return False

        password, ok = QInputDialog.getText(
            self,
            "Authentification",
            "Entrez le mot de passe pour continuer :",
            QLineEdit.Password
        )
        if ok and password == self.parent_window.password:
            return True
        elif ok:
            QMessageBox.warning(self, "Erreur", "Mot de passe incorrect !")
        return False

    def modify_expense(self, row):
        expense_type = self.table.item(row, 0).text()
        amount = float(self.table.item(row, 1).text())
        expense_date = self.table.item(row, 2).text()

        dialog = ModifyExpenseDialog(expense_type, amount, expense_date, self)
        if dialog.exec():
            new_expense_type, new_amount, new_expense_date = dialog.get_data()
            if new_expense_type and new_amount is not None:
                try:
                    connection = sqlite3.connect("gestion_meca.db")
                    cursor = connection.cursor()
                    cursor.execute(
                        "UPDATE expenses SET expense_type = ?, amount = ?, expense_date = ? WHERE expense_type = ? AND expense_date = ?",
                        (new_expense_type, new_amount, new_expense_date, expense_type, expense_date),
                    )
                    connection.commit()
                    connection.close()
                    self.load_data()  # Aggiorna la tabella dopo la modifica
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification de la dépense : {str(e)}")

    def delete_expense(self, row):
        expense_type = self.table.item(row, 0).text()
        expense_date = self.table.item(row, 2).text()

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous supprimer cette dépense ({expense_type} - {expense_date}) ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirmation == QMessageBox.Yes:
            try:
                connection = sqlite3.connect("gestion_meca.db")
                cursor = connection.cursor()
                cursor.execute(
                    "DELETE FROM expenses WHERE expense_type = ? AND expense_date = ?", (expense_type, expense_date)
                )
                connection.commit()
                connection.close()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression de la dépense : {str(e)}")
