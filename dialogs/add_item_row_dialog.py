from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialogButtonBox
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator

class AddItemRowDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une ligne")
        self.setMinimumSize(400, 250)  # Dimensioni del dialog

        # Layout principale
        layout = QVBoxLayout()

        # Form per i dettagli della riga
        form_layout = QFormLayout()

        # Campo per il nome dell'articolo
        self.article_name_input = QLineEdit()
        self.article_name_input.setPlaceholderText("Exemple: Roue, Huile, etc.")
        self.article_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #2E86C1;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Nom de l'article:", self.article_name_input)

        # Campo per la quantità
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, 9999))  # Validatore numerico
        self.quantity_input.setTextMargins(10, 5, 10, 5)  # Margine interno
        self.quantity_input.setPlaceholderText("Exemple: 10")
        self.quantity_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #FFA07A;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                text-align: right; /* Allinea il testo a destra */
            }
        """)
        form_layout.addRow("Quantité:", self.quantity_input)

        # Campo per il montante totale
        self.total_amount_input = QLineEdit()
        self.total_amount_input.setValidator(QDoubleValidator(0.01, 999999.99, 2))  # Validatore numerico
        self.total_amount_input.setTextMargins(10, 5, 10, 5)  # Margine interno
        self.total_amount_input.setPlaceholderText("Exemple: 1234.56 CFA")
        self.total_amount_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #2E86C1;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                text-align: right; /* Allinea il testo a destra */
            }
        """)
        form_layout.addRow("Montant Total (CFA):", self.total_amount_input)

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
        """Restituisce i dati inseriti dall'utente."""
        article_name = self.article_name_input.text().strip()
        quantity = int(self.quantity_input.text())
        total_amount = float(self.total_amount_input.text())
        return article_name, quantity, total_amount