from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFormLayout, QLabel, QHBoxLayout, QMessageBox, QHeaderView, QGroupBox, QSpinBox, QDoubleSpinBox, QAbstractSpinBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class CartDialog(QDialog):
    def __init__(self, cart, parent=None):
        super().__init__(parent)
        self.cart = cart
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Panier")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Tabella del carrello
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Article", "Prix", "Qté", "Remise", "Total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")

        # Popola la tabella con gli articoli nel carrello
        total = 0
        for item in self.cart:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)

            price = float(item['sale_price'])
            qty = int(item['quantity_sold'])
            discount = float(item['discount'])
            item_total = price * qty * (1 - discount/100)

            self.cart_table.setItem(row, 0, QTableWidgetItem(item['article_name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{price:.2f} CFA"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(qty)))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{discount}%"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{item_total:.2f} CFA"))

            total += item_total

        # Aggiungi una riga per il totale
        self.cart_table.setRowCount(self.cart_table.rowCount() + 1)
        total_row = self.cart_table.rowCount() - 1
        self.cart_table.setItem(total_row, 0, QTableWidgetItem("Total"))
        self.cart_table.setItem(total_row, 4, QTableWidgetItem(f"{total:.2f} CFA"))

        # Formattazione della riga totale
        for col in range(5):
            cell = self.cart_table.item(total_row, col)
            if cell:
                cell.setFont(QFont("Arial", 14, QFont.Bold))
                cell.setForeground(Qt.red) if col == 4 else cell.setForeground(Qt.black)

        layout.addWidget(self.cart_table)

        # Pulsanti per le azioni
        button_layout = QHBoxLayout()
        
        modify_button = QPushButton("Modifier")
        modify_button.setStyleSheet("background-color: #FFA500; color: white; border: none; border-radius: 5px; padding: 10px 20px;")
        modify_button.clicked.connect(self.modify_item)
        button_layout.addWidget(modify_button)
        
        remove_button = QPushButton("Supprimer")
        remove_button.setStyleSheet("background-color: #FF0000; color: white; border: none; border-radius: 5px; padding: 10px 20px;")
        remove_button.clicked.connect(self.remove_item)
        button_layout.addWidget(remove_button)
        
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("background-color: #2E86C1; color: white; border: none; border-radius: 5px; padding: 10px 20px;")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def modify_item(self):
        selected_row = self.cart_table.currentRow()
        if selected_row < 0 or selected_row >= len(self.cart):
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à modifier.")
            return
            
        item = self.cart[selected_row]
        
        # Crea un dialogo personalizzato per la modifica
        dialog = QDialog(self) # Parent è self (CartDialog)
        dialog.setWindowTitle(f"Modifier l'article : {item['article_name']}") # Titolo più specifico
        dialog.setMinimumWidth(450) # Leggermente più largo
        dialog.setMinimumHeight(300) # Altezza minima

        main_dialog_layout = QVBoxLayout(dialog) # Imposta il layout direttamente sul dialogo
        main_dialog_layout.setContentsMargins(15, 15, 15, 15) # Margini
        main_dialog_layout.setSpacing(10) # Spaziatura

        # Gruppo per i campi di input
        details_group = QGroupBox("Détails de l'article")
        details_group.setFont(QFont("Arial", 10, QFont.Bold)) # Font per il titolo del gruppo
        form_layout = QFormLayout(details_group) # Layout del gruppo
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight) # Allinea etichette a destra

        # Stile per le etichette del form
        label_style = "QLabel { font-weight: bold; font-size: 10pt; }"
        
        # Stile comune per i campi di input
        input_style = """
            QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ccc; /* Bordo più sottile */
                border-radius: 4px;
                background-color: white;
                font-size: 10pt; /* Dimensione font consistente */
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #2E86C1; /* Bordo blu al focus */
            }
        """
        
        # Campo quantità
        quantity_label = QLabel("Quantité:")
        quantity_label.setStyleSheet(label_style)
        quantity_input = QSpinBox()
        quantity_input.setRange(1, 9999)
        quantity_input.setValue(item['quantity_sold'])
        quantity_input.setStyleSheet(input_style)
        form_layout.addRow(quantity_label, quantity_input)
        
        # Campo prezzo
        price_input = QDoubleSpinBox()
        price_input.setRange(0.01, 999999.99)
        price_input.setDecimals(2)
        price_input.setValue(item['sale_price'])
        price_input.setSuffix(" CFA")
        price_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # Rimuove i pulsantini up/down
        price_input.setStyleSheet(input_style)
        price_label = QLabel("Prix Unitaire (CFA):") # Etichetta più chiara
        price_label.setStyleSheet(label_style)
        form_layout.addRow(price_label, price_input)
        
        # Campo sconto
        discount_input = QDoubleSpinBox()
        discount_input.setRange(0, 100)
        discount_input.setDecimals(2)
        discount_input.setValue(item['discount'])
        # discount_input.setSuffix("%") # Rimosso il suffisso, l'etichetta lo indica
        discount_input.setButtonSymbols(QAbstractSpinBox.NoButtons) # Rimuove i pulsantini up/down
        discount_input.setStyleSheet(input_style)
        discount_label = QLabel("Remise (%):")
        discount_label.setStyleSheet(label_style)
        form_layout.addRow(discount_label, discount_input)

        main_dialog_layout.addWidget(details_group) # Aggiungi il gruppo al layout principale
        
        # Pulsanti
        button_box_layout = QHBoxLayout() # Layout per i pulsanti
        button_box_layout.addStretch() # Spinge i pulsanti a destra
        
        save_button = QPushButton("Enregistrer")
        save_button.setFont(QFont("Arial", 10, QFont.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838; /* Verde più scuro per hover */
            }
        """)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.setFont(QFont("Arial", 10))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6268; /* Grigio più scuro per hover */
            }
        """)
        
        button_box_layout.addWidget(save_button)
        button_box_layout.addWidget(cancel_button)
        main_dialog_layout.addLayout(button_box_layout) # Aggiungi il layout dei pulsanti
        
        # Connetti i pulsanti
        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Mostra il dialogo
        if dialog.exec() == QDialog.Accepted:
            # Aggiorna il carrello con i nuovi valori
            self.cart[selected_row].update({
                'quantity_sold': quantity_input.value(),
                'sale_price': price_input.value(),
                'discount': discount_input.value()
            })
            
            # Aggiorna la tabella
            price = price_input.value()
            qty = quantity_input.value()
            discount = discount_input.value()
            
            self.cart_table.setItem(selected_row, 1, QTableWidgetItem(f"{price:.2f} CFA"))
            self.cart_table.setItem(selected_row, 2, QTableWidgetItem(str(qty)))
            self.cart_table.setItem(selected_row, 3, QTableWidgetItem(f"{discount}%"))
            
            item_total = price * qty * (1 - discount/100)
            self.cart_table.setItem(selected_row, 4, QTableWidgetItem(f"{item_total:.2f} CFA"))
            
            # Aggiorna il totale
            self.update_total()
        # Il blocco di codice ridondante che era qui è stato rimosso.
        
    def remove_item(self):
        selected_row = self.cart_table.currentRow()
        if selected_row < 0 or selected_row >= len(self.cart):
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un article à supprimer.")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer cet article du panier ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart.pop(selected_row)
            self.cart_table.removeRow(selected_row)
            self.update_total()
            
    def update_total(self):
        total = 0
        for item in self.cart:
            price = float(item['sale_price'])
            qty = int(item['quantity_sold'])
            discount = float(item['discount'])
            item_total = price * qty * (1 - discount/100)
            total += item_total
            
        # Aggiorna la riga del totale
        total_row = self.cart_table.rowCount() - 1
        self.cart_table.setItem(total_row, 4, QTableWidgetItem(f"{total:.2f} CFA"))
