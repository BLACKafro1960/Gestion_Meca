from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout
from PySide6.QtGui import QFont

class AddItemDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ajouter un Article")
        self.setMinimumSize(400, 300)
        self.layout = QGridLayout()

        self.name_label = QLabel("Nom de l'Article :")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label, 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)

        self.purchase_price_label = QLabel("Prix d'Achat (CFA) :")
        self.purchase_price_input = QLineEdit()
        self.layout.addWidget(self.purchase_price_label, 1, 0)
        self.layout.addWidget(self.purchase_price_input, 1, 1)

        self.sale_price_label = QLabel("Prix de Vente (CFA) :")
        self.sale_price_input = QLineEdit()
        self.layout.addWidget(self.sale_price_label, 2, 0)
        self.layout.addWidget(self.sale_price_input, 2, 1)

        self.quantity_label = QLabel("Quantité :")
        self.quantity_input = QLineEdit()
        self.layout.addWidget(self.quantity_label, 3, 0)
        self.layout.addWidget(self.quantity_input, 3, 1)

        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("Ajouter")
        self.submit_button.clicked.connect(self.submit)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout, 4, 0, 1, 2)
        self.setLayout(self.layout)
        self.result_data = None

    def submit(self):
        try:
            article_name = self.name_input.text().strip()
            purchase_price = float(self.purchase_price_input.text().strip())
            sale_price = float(self.sale_price_input.text().strip())
            quantity = int(self.quantity_input.text().strip())

            if not article_name or purchase_price <= 0 or sale_price <= 0 or quantity <= 0:
                raise ValueError

            self.result_data = (article_name, purchase_price, sale_price, quantity)
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs valides!")

    def get_data(self):
        return self.result_data
