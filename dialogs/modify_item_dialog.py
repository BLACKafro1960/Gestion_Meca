from PySide6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout
from PySide6.QtGui import QFont

class ModifyItemDialog(QDialog):
    def __init__(self, article_name):
        super().__init__()
        self.setWindowTitle("Modifier ou Supprimer l'Article")
        self.setMinimumSize(400, 300)
        self.article_name = article_name
        self.layout = QGridLayout()

        self.info_label = QLabel(f"Modification de l'article : {article_name}")
        self.layout.addWidget(self.info_label, 0, 0, 1, 2)

        self.purchase_price_label = QLabel("Nouveau Prix d'Achat (CFA) :")
        self.purchase_price_input = QLineEdit()
        self.layout.addWidget(self.purchase_price_label, 1, 0)
        self.layout.addWidget(self.purchase_price_input, 1, 1)

        self.sale_price_label = QLabel("Nouveau Prix de Vente (CFA) :")
        self.sale_price_input = QLineEdit()
        self.layout.addWidget(self.sale_price_label, 2, 0)
        self.layout.addWidget(self.sale_price_input, 2, 1)

        self.quantity_label = QLabel("Nouvelle Quantité :")
        self.quantity_input = QLineEdit()
        self.layout.addWidget(self.quantity_label, 3, 0)
        self.layout.addWidget(self.quantity_input, 3, 1)

        button_layout = QHBoxLayout()
        self.modify_button = QPushButton("Modifier")
        self.modify_button.clicked.connect(self.modify)
        button_layout.addWidget(self.modify_button)

        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete)
        button_layout.addWidget(self.delete_button)

        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout, 4, 0, 1, 2)
        self.setLayout(self.layout)
        self.result_action = None
        self.result_data = None

    def modify(self):
        try:
            purchase_price = float(self.purchase_price_input.text().strip())
            sale_price = float(self.sale_price_input.text().strip())
            quantity = int(self.quantity_input.text().strip())

            if purchase_price <= 0 or sale_price <= 0 or quantity <= 0:
                raise ValueError

            self.result_action = "modify"
            self.result_data = (purchase_price, sale_price, quantity)
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs valides!")

    def delete(self):
        self.result_action = "delete"
        self.accept()

    def get_data(self):
        return self.result_action, self.result_data
