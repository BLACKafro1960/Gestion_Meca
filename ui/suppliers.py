from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QInputDialog, QHeaderView, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class SuppliersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent  # Salva il riferimento alla finestra principale
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Campo di ricerca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(placeholderText="Rechercher un fournisseur...")
        self.search_input.textChanged.connect(self.filter_suppliers)
        search_layout.addWidget(QLabel("Rechercher:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Tabella fornitori
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Nome, Contatti, Azioni
        self.table.setHorizontalHeaderLabels(["Nom du Fournisseur", "Coordonnées", "Actions"])
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

        # Pulsante "Ajouter un Fournisseur"
        add_supplier_button = QPushButton("Ajouter un Fournisseur")
        add_supplier_button.setStyleSheet("""
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
        add_supplier_button.clicked.connect(self.add_supplier)
        layout.addWidget(add_supplier_button)

        # Pulsante "Exporter en PDF"
        export_pdf_button = QPushButton("Exporter Liste des Fournisseurs en PDF")
        export_pdf_button.setStyleSheet("""
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
        export_pdf_button.clicked.connect(self.export_to_pdf)
        layout.addWidget(export_pdf_button)

        self.setLayout(layout)

        # Carica i dati dalla tabella dei fornitori
        self.load_data()

    def load_data(self):
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT supplier_name, contact_info FROM suppliers")
            rows = cursor.fetchall()
            connection.close()

            self.table.setRowCount(0)  # Resetta la tabella
            for row_data in rows:
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_number, column_number, item)

                # Aggiungi pulsanti Modifica e Elimina
                modify_button = QPushButton("Modifier")
                modify_button.setStyleSheet("background-color: #90EE90;")
                modify_button.clicked.connect(lambda _, r=row_number: self.modify_supplier(r))
                delete_button = QPushButton("Supprimer")
                delete_button.setStyleSheet("background-color: #FF4500; color: white;")
                delete_button.clicked.connect(lambda _, r=row_number: self.delete_supplier(r))

                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.addWidget(modify_button)
                actions_layout.addWidget(delete_button)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setAlignment(Qt.AlignCenter)

                self.table.setCellWidget(row_number, 2, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Erreur Chargement", f"Erreur lors du chargement des fournisseurs : {str(e)}")

    def filter_suppliers(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            supplier_name_item = self.table.item(row, 0)
            if supplier_name_item:
                supplier_name = supplier_name_item.text().lower()
                self.table.setRowHidden(row, search_text not in supplier_name)

    def add_supplier(self):
        name, ok = QInputDialog.getText(self, "Nouveau Fournisseur", "Nom du fournisseur:")
        if not ok or not name.strip():
            return

        contact_info, ok = QInputDialog.getText(self, "Nouveau Fournisseur", "Informations de contact (téléphone, adresse, etc.):")
        if not ok:
            return

        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO suppliers (supplier_name, contact_info) VALUES (?, ?)", (name, contact_info))
            connection.commit()
            connection.close()
            self.load_data()  # Aggiorna la tabella dopo l'inserimento
            QMessageBox.information(self, "Succès", "Le fournisseur a été ajouté avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ajout du fournisseur : {str(e)}")

    def request_password(self):
        """Richiede la password prima di consentire modifiche o eliminazioni."""
        if not hasattr(self.parent_window, 'password'):
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

    def modify_supplier(self, row):
        if not self.request_password():
            return

        supplier_name = self.table.item(row, 0).text()
        contact_info = self.table.item(row, 1).text()

        new_name, ok = QInputDialog.getText(self, "Modifier Fournisseur", "Nouveau nom:", text=supplier_name)
        if not ok or not new_name.strip():
            return

        new_contact_info, ok = QInputDialog.getText(self, "Modifier Fournisseur", "Nouvelles informations de contact:", text=contact_info)
        if not ok:
            return

        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("UPDATE suppliers SET supplier_name = ?, contact_info = ? WHERE supplier_name = ?", (new_name, new_contact_info, supplier_name))
            connection.commit()
            connection.close()
            self.load_data()  # Aggiorna la tabella dopo la modifica
            QMessageBox.information(self, "Succès", "Le fournisseur a été modifié avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification du fournisseur : {str(e)}")

    def delete_supplier(self, row):
        if not self.request_password():
            return

        supplier_name = self.table.item(row, 0).text()
        confirmation = QMessageBox.question(self, "Confirmation", f"Voulez-vous supprimer le fournisseur '{supplier_name}' ?", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            try:
                connection = sqlite3.connect("gestion_meca.db")
                cursor = connection.cursor()
                cursor.execute("DELETE FROM suppliers WHERE supplier_name = ?", (supplier_name,))
                connection.commit()
                connection.close()
                self.load_data()  # Aggiorna la tabella dopo l'eliminazione
                QMessageBox.information(self, "Succès", "Le fournisseur a été supprimé avec succès.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression du fournisseur : {str(e)}")

    def export_to_pdf(self):
        try:
            connection = sqlite3.connect("gestion_meca.db")
            cursor = connection.cursor()
            cursor.execute("SELECT supplier_name, contact_info FROM suppliers")
            rows = cursor.fetchall()
            connection.close()

            pdf_file_name = f"liste_fournisseurs_{datetime.now().strftime('%d-%m-%Y')}.pdf"
            doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Titolo
            title = Paragraph("Liste des Fournisseurs", styles["Title"])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Tabella fornitori
            data = [["Nom du Fournisseur", "Coordonnées"]]
            for row in rows:
                data.append([row[0], row[1]])

            table = Table(data, colWidths=[300, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(table)

            doc.build(elements)
            QMessageBox.information(self, "Succès", f"La liste des fournisseurs a été exportée en PDF : {pdf_file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'exportation en PDF : {str(e)}")
