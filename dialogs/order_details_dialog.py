from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class OrderDetailsDialog(QDialog):
    def __init__(self, order_id, order_details, items):
        super().__init__()
        self.setWindowTitle(f"Détails de l'Ordre {order_id}")
        self.setMinimumSize(800, 600)  # Dimensioni aumentate per maggiore chiarezza

        # Layout principale
        layout = QVBoxLayout()

        # Titolo dell'ordine
        title_label = QLabel(f"Détails de l'Ordre {order_id}")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E86C1; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # Informazioni generali sull'ordine
        details_group = QGroupBox("Informations Générales")
        details_layout = QFormLayout()

        # Stili per le label
        label_style = "QLabel { font-weight: bold; color: #333; }"

        # ID Ordine
        id_label = QLabel(order_id)
        id_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addRow(QLabel("ID Ordine:", objectName="boldLabel"), id_label)

        # Fornitore
        supplier_label = QLabel(order_details[0])
        supplier_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addRow(QLabel("Fournisseur:", objectName="boldLabel"), supplier_label)

        # Data di Comando
        order_date_label = QLabel(order_details[1])
        order_date_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addRow(QLabel("Date de Commande:", objectName="boldLabel"), order_date_label)

        # Data di Consegna Prevista
        delivery_date_label = QLabel(order_details[2] if order_details[2] else "Non spécifiée")
        delivery_date_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addRow(QLabel("Date de Livraison Prévue:", objectName="boldLabel"), delivery_date_label)

        # Stato
        status_label = QLabel(order_details[3])
        status_label.setStyleSheet("font-size: 14px; color: #555;")
        details_layout.addRow(QLabel("Statut:", objectName="boldLabel"), status_label)

        # Applica lo stile alle label bold
        for i in range(details_layout.count()):
            item = details_layout.itemAt(i)
            if isinstance(item, QLayoutItem):
                widget = item.widget()
                if isinstance(widget, QLabel) and widget.objectName() == "boldLabel":
                    widget.setStyleSheet(label_style)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Tabella delle righe dell'ordine
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)  # Aggiunta colonna "Prix Unitaire"
        self.items_table.setHorizontalHeaderLabels(["Article", "Quantité", "Prix Unitaire (CFA)", "Montant Total (CFA)"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                margin: 10px 0;
                font-size: 14px;
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

        # Popolamento della tabella
        total_order_amount = 0  # Calcolo del totale dell'ordine
        for item in items:
            row_number = self.items_table.rowCount()
            self.items_table.insertRow(row_number)

            article_name = QTableWidgetItem(item[0])
            quantity = QTableWidgetItem(str(item[1]))
            unit_price = float(item[2]) / item[1] if item[1] > 0 else 0  # Calcolo prezzo unitario
            total_amount = QTableWidgetItem(f"{item[2]:.2f}")

            # Imposta i valori nella tabella
            self.items_table.setItem(row_number, 0, article_name)
            self.items_table.setItem(row_number, 1, quantity)
            self.items_table.setItem(row_number, 2, QTableWidgetItem(f"{unit_price:.2f}"))
            self.items_table.setItem(row_number, 3, total_amount)

            # Aggiorna il totale dell'ordine
            total_order_amount += item[2]

        # Aggiungi riga per il totale
        self.items_table.setRowCount(self.items_table.rowCount() + 1)
        total_row = self.items_table.rowCount() - 1
        self.items_table.setItem(total_row, 0, QTableWidgetItem("Total de l'Ordre"))
        self.items_table.setItem(total_row, 3, QTableWidgetItem(f"{total_order_amount:.2f}"))

        # Formattazione della riga totale
        for col in range(4):
            cell = self.items_table.item(total_row, col)
            if cell:
                cell.setFont(QFont("Arial", 14, QFont.Bold))
                cell.setForeground(Qt.red) if col == 3 else cell.setForeground(Qt.black)

        layout.addWidget(self.items_table)

        # Pulsante di chiusura
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1B4F72;
            }
        """)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        # Imposta il layout
        self.setLayout(layout)
