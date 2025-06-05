from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QDateEdit, QDialogButtonBox, QMessageBox
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import QDate

class AddExpenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une Dépense")
        self.setMinimumSize(400, 250)  # Dimensioni del dialog

        # Layout principale
        layout = QVBoxLayout()

        # Form per i dettagli della spesa
        form_layout = QFormLayout()

        # Campo per il tipo di spesa
        self.expense_type_input = QLineEdit()
        self.expense_type_input.setPlaceholderText("Exemple: Électricité, Loyer, etc.")
        self.expense_type_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #2E86C1;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Type de dépense:", self.expense_type_input)

        # Campo per l'importo
        self.amount_input = QLineEdit()
        self.amount_input.setValidator(QDoubleValidator(0.01, 999999.99, 2))  # Validatore numerico
        self.amount_input.setTextMargins(10, 5, 10, 5)  # Margine interno
        self.amount_input.setPlaceholderText("Exemple: 1234.56 CFA")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #FFA07A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                text-align: right; /* Allinea il testo a destra */
            }
        """)
        form_layout.addRow("Montant (CFA):", self.amount_input)

        # Campo per la data (opzionale)
        self.expense_date_input = QDateEdit()
        self.expense_date_input.setDate(QDate.currentDate())  # Imposta la data corrente
        self.expense_date_input.setCalendarPopup(True)  # Mostra il calendario popup
        self.expense_date_input.setStyleSheet("""
            QDateEdit {
                border: 1px solid #2E86C1;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Date:", self.expense_date_input)

        # Aggiungi il form al layout principale
        layout.addLayout(form_layout)

        # Pulsanti OK e Annulla
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("""
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
        layout.addWidget(button_box)

        # Imposta il layout
        self.setLayout(layout)

    def get_data(self):
        expense_type = self.expense_type_input.text().strip()
        amount_text = self.amount_input.text().strip()
        expense_date = self.expense_date_input.date().toString("dd-MM-yyyy")  # Formatta la data

        if not expense_type:
            QMessageBox.warning(self, "Erreur", "Le type de dépense ne peut pas être vide.")
            return None, None, None

        try:
            if not amount_text:
                QMessageBox.warning(self, "Erreur", "Le montant ne peut pas être vide.")
                return None, None, None

            amount = float(amount_text)
            if amount <= 0:
                QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0.")
                return None, None, None

            return expense_type, amount, expense_date
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un montant valide (exemple: 1234.56).")
            return None, None, None
