from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QListWidget, QListWidgetItem, QFormLayout, QMessageBox, QGroupBox, QComboBox, QDialog
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, QDate
import sqlite3
from datetime import datetime
from dialogs.cart_dialog import CartDialog

class SalesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.cart = []
        self.setup_ui()

    def setup_ui(self):
        # Layout principale
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Colonna sinistra (ricerca e lista articoli)
        left_column = QVBoxLayout()
        left_column.setSpacing(15)

        # Titolo della pagina
        title_label = QLabel("Gestion des Ventes")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E86C1; margin-bottom: 20px;")
        left_column.addWidget(title_label)

        # Sezione di ricerca
        search_group = QGroupBox("Rechercher Article")
        search_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #2E86C1;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
            QGroupBox::title {
                color: #2E86C1;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        search_layout = QVBoxLayout()

        self.article_search_input = QLineEdit(placeholderText="🔍 Entrez le nom de l'article...")
        self.article_search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #2E86C1;
                background-color: white;
            }
        """)
        self.article_search_input.textChanged.connect(self.filter_articles)
        search_layout.addWidget(self.article_search_input)

        self.article_list = QListWidget()
        self.article_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 5px;
                background-color: white;
                min-height: 300px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #2E86C1;
                color: white;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        self.article_list.itemClicked.connect(self.select_article)
        search_layout.addWidget(self.article_list)

        search_group.setLayout(search_layout)
        left_column.addWidget(search_group)

        # Colonna destra (dettagli vendita e azioni)
        right_column = QVBoxLayout()
        right_column.setSpacing(15)

        # Sezione dettagli della vendita
        form_group = QGroupBox("Détails de la Vente")
        form_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
            QGroupBox::title {
                color: #4CAF50;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.sales_form = QFormLayout()
        self.sales_form.setSpacing(12)

        # Stile comune per i campi di input
        input_style = """
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            background-color: #f8f9fa;
        """

        # Dettagli dell'articolo
        self.article_name_input = QLineEdit()
        self.article_name_input.setReadOnly(True)
        self.article_name_input.setStyleSheet(input_style)
        self.sales_form.addRow("Article:", self.article_name_input)

        self.quantity_sold_input = QLineEdit()
        self.quantity_sold_input.setValidator(QIntValidator(1, 9999))
        self.quantity_sold_input.setStyleSheet(input_style)
        self.sales_form.addRow("Quantité:", self.quantity_sold_input)

        self.sale_price_input = QLineEdit()
        self.sale_price_input.setValidator(QDoubleValidator(0.01, 999999.99, 2))
        self.sale_price_input.setStyleSheet(input_style)
        self.sales_form.addRow("Prix Unitaire (CFA):", self.sale_price_input)

        self.discount_input = QLineEdit("0")
        self.discount_input.setValidator(QDoubleValidator(0, 100, 2))
        self.discount_input.setStyleSheet(input_style)
        self.sales_form.addRow("Remise (%):", self.discount_input)

        # Dettagli del cliente
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setStyleSheet(input_style)
        self.sales_form.addRow("Client:", self.customer_name_input)

        self.payment_method_input = QComboBox()
        self.payment_method_input.addItems(["Espèces", "Carte", "Mobile Money", "Chèque"])
        self.payment_method_input.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.sales_form.addRow("Méthode de Paiement:", self.payment_method_input)

        # Pulsanti azione
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)

        self.add_to_cart_button = QPushButton("➕ Ajouter au Panier")
        self.add_to_cart_button.setStyleSheet("""
            QPushButton {
                background-color: #2E86C1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a5f8c;
            }
        """)
        self.add_to_cart_button.clicked.connect(self.add_to_cart)
        buttons_layout.addWidget(self.add_to_cart_button)

        self.view_cart_button = QPushButton("🛒 Voir le Panier")
        self.view_cart_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA07A;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7f50;
            }
        """)
        self.view_cart_button.clicked.connect(self.show_cart)
        buttons_layout.addWidget(self.view_cart_button)

        self.record_sale_button = QPushButton("💾 Enregistrer la Vente")
        self.record_sale_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        self.record_sale_button.clicked.connect(self.record_sale)
        buttons_layout.addWidget(self.record_sale_button)

        form_group.setLayout(self.sales_form)
        right_column.addWidget(form_group)
        right_column.addLayout(buttons_layout)

        # Aggiunta delle colonne al layout principale
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        left_widget.setFixedWidth(400)

        right_widget = QWidget()
        right_widget.setLayout(right_column)

        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)

    def update_cart_total(self):
        try:
            total = 0
            for item in self.cart:
                price = float(item['sale_price'])
                qty = int(item['quantity_sold'])
                discount = float(item['discount'])
                item_total = price * qty * (1 - discount/100)
                total += item_total
            if hasattr(self, 'total_label'):
                self.total_label.setText(f"Total: {total:.2f} CFA")
            return total
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la mise à jour du total: {str(e)}")
            return 0

    def filter_articles(self):
        search_text = self.article_search_input.text().strip().lower()
        if not search_text:
            self.article_list.clear()
            return

        try:
            with sqlite3.connect("gestion_meca.db") as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT article_name, sale_price, quantity FROM articles WHERE article_name LIKE ?",
                    (f"%{search_text}%",)
                )
                results = cursor.fetchall()

            self.article_list.clear()
            for row in results:
                item = QListWidgetItem(f"{row[0]} - Prix: {row[1]} CFA - Quantité: {row[2]}")
                item.setData(Qt.UserRole, row[0])
                self.article_list.addItem(item)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

    def select_article(self, item):
        article_name = item.data(Qt.UserRole)

        with sqlite3.connect("gestion_meca.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT sale_price, quantity FROM articles WHERE article_name = ?", (article_name,))
            result = cursor.fetchone()

        if result:
            self.article_name_input.setText(article_name)
            self.sale_price_input.setText(str(result[0]))
            QMessageBox.information(self, "Quantité disponible", f"Quantité disponible: {result[1]}")

    def validate_stock(article_name, quantity_sold):
        connection = sqlite3.connect("gestion_meca.db")
        cursor = connection.cursor()
        cursor.execute("SELECT quantity FROM articles WHERE article_name = ?", (article_name,))
        available_quantity = cursor.fetchone()[0]
        connection.close()
        if quantity_sold > available_quantity:
            raise ValueError(f"La quantité demandée ({quantity_sold}) dépasse la quantité disponible ({available_quantity}).")

    def add_to_cart(self):
        article_name = self.article_name_input.text().strip()
        sale_price = self.sale_price_input.text().strip()
        quantity_sold = self.quantity_sold_input.text().strip()
        discount = self.discount_input.text().strip()

        if not article_name or not sale_price or not quantity_sold:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        try:
            sale_price = float(sale_price)
            quantity_sold = int(quantity_sold)
            discount = float(discount) if discount else 0

            if sale_price <= 0 or quantity_sold <= 0:
                raise ValueError

            # Aggiungi l'articolo al carrello
            self.cart.append({
                'article_name': article_name,
                'sale_price': sale_price,
                'quantity_sold': quantity_sold,
                'discount': discount
            })

            # Aggiorna il totale
            self.update_cart_total()

            # Pulisci i campi di input dopo aver aggiunto l'articolo al carrello
            self.clear_input_fields()

        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs valides.")

    def clear_input_fields(self):
        # Pulisci solo i campi di input specifici, non il totale e l'IVA
        self.article_name_input.clear()
        self.quantity_sold_input.clear()
        self.sale_price_input.clear()
        self.discount_input.clear()

    def show_cart(self):
        dialog = CartDialog(self.cart, self)
        dialog.exec()

    def record_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "Erreur", "Aucun article dans le panier.")
            return

        customer_name = self.customer_name_input.text().strip()
        sale_date = QDate.currentDate().toString("dd-MM-yyyy")
        payment_method = self.payment_method_input.currentText()

        try:
            with sqlite3.connect("gestion_meca.db") as connection:
                cursor = connection.cursor()

                for item in self.cart:
                    article_name = item['article_name']
                    quantity_sold = item['quantity_sold']
                    sale_price = item['sale_price']
                    discount = item['discount']

                    cursor.execute("SELECT sale_price, quantity FROM articles WHERE article_name = ?", (article_name,))
                    result = cursor.fetchone()

                    if not result:
                        QMessageBox.warning(self, "Erreur", f"L'article '{article_name}' n'existe pas dans l'inventaire.")
                        continue

                    registered_sale_price, available_quantity = result

                    # Controllo del prezzo di vendita
                    if sale_price < registered_sale_price:
                        QMessageBox.critical(
                            self,
                            "Erreur Prix",
                            f"Le prix de vente ({sale_price:.2f} CFA) ne peut pas être inférieur au prix d'achat ({registered_sale_price:.2f} CFA)."
                        )
                        continue

                    if quantity_sold > available_quantity:
                        QMessageBox.warning(self, "Erreur", "La quantité vendue dépasse la quantité disponible.")
                        continue
                    new_quantity = available_quantity - quantity_sold

                    if new_quantity <= 0:
                        cursor.execute("DELETE FROM articles WHERE article_name = ?", (article_name,))

                    else:
                        cursor.execute("UPDATE articles SET quantity = ? WHERE article_name = ?", (new_quantity, article_name))

                    subtotal = sale_price * quantity_sold
                    total_amount_before_tax = subtotal * (1 - discount / 100)
                    total_amount = total_amount_before_tax
                    cursor.execute(
                        "INSERT INTO sales (article_name, quantity_sold, total_amount, sale_date, customer_name, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
                        (article_name, quantity_sold, total_amount, sale_date, customer_name, payment_method)
                    )
                connection.commit()

                # Aggiorna l'inventario e il dashboard usando il riferimento al main window
                if self.main_window and hasattr(self.main_window, 'inventory_tab'):
                    self.main_window.inventory_tab.load_data()  # Aggiorna l'inventario
                if hasattr(self.main_window, 'dashboard_tab'):
                    self.main_window.dashboard_tab.update_dashboard()

            QMessageBox.information(self, "Succès", "La vente a été enregistrée avec succès.")
            self.clear_fields()
            self.cart = []  # Svuota il carrello dopo aver registrato la vendita

        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs valides.")

    def clear_fields(self):
        self.article_name_input.clear()
        self.quantity_sold_input.clear()
        self.sale_price_input.clear()
        self.discount_input.clear()
        self.customer_name_input.clear()

    def load_data(self):
        try:
            with sqlite3.connect("gestion_meca.db") as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT article_name, quantity_sold, total_amount, sale_date FROM sales ORDER BY sale_date DESC LIMIT 10")
                sales_data = cursor.fetchall()

            for row_data in sales_data:
                print(f"Vendita: {row_data[0]}, Quantità: {row_data[1]}, Totale: {row_data[2]}, Data: {row_data[3]}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les données des ventes : {str(e)}")
