from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QInputDialog, QLabel, QComboBox
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit # Importa QLineEdit per il QInputDialog password
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import csv
import pandas as pd
import logging
from PySide6.QtCore import QUrl, QTimer # Importa QTimer
from PySide6.QtWidgets import QSizePolicy # Importa QSizePolicy
import os
from config import DATABASE_PATH, REPORT_DIR # Importa le costanti di configurazione

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.parent_window = None # Sarà impostato dalla main window

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Titolo della pagina
        title_label = QLabel("Gestion des Rapports")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E86C1; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Pulsanti per generare i rapporti
        # button_layout = QHBoxLayout() # Variabile non utilizzata, report_options_layout è usata al suo posto
        report_options_layout = QHBoxLayout()

        self.daily_report_button = QPushButton("Rapport Journalier")
        self.daily_report_button.clicked.connect(lambda: self.generate_report("daily"))
        report_options_layout.addWidget(self.daily_report_button)

        self.weekly_report_button = QPushButton("Rapport Hebdomadaire")
        self.weekly_report_button.clicked.connect(lambda: self.generate_report("weekly"))
        report_options_layout.addWidget(self.weekly_report_button)

        self.monthly_report_button = QPushButton("Rapport Mensuel")
        self.monthly_report_button.clicked.connect(lambda: self.generate_report("monthly"))
        report_options_layout.addWidget(self.monthly_report_button)

        self.yearly_report_button = QPushButton("Rapport Annuel")
        self.yearly_report_button.clicked.connect(lambda: self.generate_report("yearly"))
        report_options_layout.addWidget(self.yearly_report_button)

        self.custom_report_button = QPushButton("Recherche Avancée")
        self.custom_report_button.clicked.connect(self.generate_custom_report)
        report_options_layout.addWidget(self.custom_report_button)

        layout.addLayout(report_options_layout)

        # Selezione formato export
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Format d'exportation:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "CSV", "XLSX"])
        export_layout.addWidget(self.format_combo)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        # Sezione Backup e Ripristino
        backup_restore_layout = QHBoxLayout()
        backup_restore_layout.setSpacing(10)

        self.manual_backup_button = QPushButton("Créer un Backup Manuel")
        self.manual_backup_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #21618C;
            }
        """)
        self.manual_backup_button.clicked.connect(self.create_manual_backup)
        backup_restore_layout.addWidget(self.manual_backup_button)

        self.restore_backup_button = QPushButton("Restaurer un Backup")
        self.restore_backup_button.clicked.connect(self.request_password_for_restore)
        backup_restore_layout.addWidget(self.restore_backup_button)

        layout.addLayout(backup_restore_layout)
        self.setLayout(layout)

    def generate_custom_report(self):
        """Genera un rapporto personalizzato basato su un intervallo di date."""
        start_date, ok = QInputDialog.getText(self, "Recherche Avancée", "Date de début (jj-mm-aaaa):")
        if not ok:
            return

        end_date, ok = QInputDialog.getText(self, "Recherche Avancée", "Date de fin (jj-mm-aaaa):")
        if not ok:
            return

        try:
            datetime.strptime(start_date, "%d-%m-%Y")
            datetime.strptime(end_date, "%d-%m-%Y")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Format de date incorrect. Utilisez jj-mm-aaaa.")
            return

        self.generate_report("custom", start_date=start_date, end_date=end_date)

    def generate_report(self, report_type, start_date=None, end_date=None):
        """Genera il rapporto nel formato selezionato."""
        export_format = self.format_combo.currentText().lower()
        today = datetime.now()

        # Variabili per le date da usare nelle query SQL (formato YYYY-MM-DD)
        db_start_date_str = ""
        db_end_date_str = ""


        # Determina l'intervallo di date in base al tipo di rapporto
        if report_type == "custom":
            if not start_date or not end_date:
                QMessageBox.warning(self, "Erreur", "Les dates de début et de fin sont requises pour une recherche avancée.")
                return
        else:
            end_date = today.strftime("%d-%m-%Y")
            if report_type == "daily":
                start_date = today.strftime("%d-%m-%Y")
            elif report_type == "weekly":
                start_of_week = today - timedelta(days=today.weekday())  # Lunedì della settimana corrente
                start_date = start_of_week.strftime("%d-%m-%Y")
                # end_date = today.strftime("%d-%m-%Y") # Già definito sopra
            elif report_type == "monthly":
                start_date = today.replace(day=1).strftime("%d-%m-%Y")  # Primo giorno del mese
                # end_date = today.strftime("%d-%m-%Y") # Già definito sopra
            elif report_type == "yearly":
                start_date = today.replace(month=1, day=1).strftime("%d-%m-%Y")  # 1° gennaio
                # end_date = today.strftime("%d-%m-%Y") # Già definito sopra

        try:
            # Converti le date stringa (dd-mm-yyyy) in formato YYYY-MM-DD per le query SQL
            db_start_date_str = datetime.strptime(start_date, "%d-%m-%Y").strftime("%Y-%m-%d")
            db_end_date_str = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")

            # Connessione al database
            connection = sqlite3.connect(DATABASE_PATH) # Usa DATABASE_PATH da config
            cursor = connection.cursor()

            # Calcola le vendite totali
            cursor.execute("""
                SELECT SUM(total_amount)
                FROM sales
                WHERE substr(sale_date, 7, 4) || '-' || substr(sale_date, 4, 2) || '-' || substr(sale_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            total_sales = cursor.fetchone()[0] or 0

            # Calcola il costo totale degli articoli venduti
            cursor.execute("""
                SELECT SUM(sales.quantity_sold * articles.purchase_price)
                FROM sales
                JOIN articles ON sales.article_name = articles.article_name
                WHERE substr(sales.sale_date, 7, 4) || '-' || substr(sales.sale_date, 4, 2) || '-' || substr(sales.sale_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            total_purchase_cost = cursor.fetchone()[0] or 0

            # Calcola le spese totali
            cursor.execute("""
                SELECT SUM(amount)
                FROM expenses
                WHERE substr(expense_date, 7, 4) || '-' || substr(expense_date, 4, 2) || '-' || substr(expense_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            total_expenses = cursor.fetchone()[0] or 0

            # Calcola il profitto netto
            net_profit = total_sales - total_purchase_cost - total_expenses

            # Recupera i dettagli delle vendite
            # Le date nei dettagli delle vendite rimangono nel formato originale dd-MM-yyyy per la visualizzazione
            cursor.execute("""
                SELECT article_name, quantity_sold, total_amount, sale_date, customer_name
                FROM sales
                WHERE substr(sale_date, 7, 4) || '-' || substr(sale_date, 4, 2) || '-' || substr(sale_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            sales_details = cursor.fetchall()

            # Recupera i clienti unici
            cursor.execute("""
                SELECT DISTINCT customer_name
                FROM sales
                WHERE substr(sale_date, 7, 4) || '-' || substr(sale_date, 4, 2) || '-' || substr(sale_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            unique_customers = [row[0] for row in cursor.fetchall()]

            # Recupera gli ordini d'acquisto
            cursor.execute("""
                SELECT po.id, po.supplier_name, po.order_date, po.delivery_date, po.status
                FROM purchase_orders AS po
                WHERE substr(po.order_date, 7, 4) || '-' || substr(po.order_date, 4, 2) || '-' || substr(po.order_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            purchase_orders = cursor.fetchall()

            # Recupera i dettagli delle righe degli ordini d'acquisto
            purchase_order_items = {}
            for order in purchase_orders:
                order_id = order[0]
                cursor.execute("""
                    SELECT article_name, quantity, total_amount
                    FROM purchase_order_items
                    WHERE order_id = ?
                """, (order_id,))
                purchase_order_items[order_id] = cursor.fetchall()

            # Recupera i fornitori coinvolti negli ordini
            cursor.execute("""
                SELECT DISTINCT supplier_name
                FROM purchase_orders
                WHERE substr(order_date, 7, 4) || '-' || substr(order_date, 4, 2) || '-' || substr(order_date, 1, 2) BETWEEN ? AND ?
            """, (db_start_date_str, db_end_date_str))
            suppliers_involved = [row[0] for row in cursor.fetchall()]

            connection.close()

            # Prepara i dati comuni per tutti i formati
            report_data = {
                'title': f"Rapport {report_type.capitalize()} du {start_date} au {end_date}",
                'total_sales': total_sales,
                'total_purchase_cost': total_purchase_cost,
                'total_expenses': total_expenses,
                'net_profit': net_profit,
                'sales_details': sales_details,
                'unique_customers': unique_customers,
                'purchase_orders': purchase_orders,
                'purchase_order_items': purchase_order_items,
                'suppliers_involved': suppliers_involved
            }

            # Assicurarsi che la directory dei report esista
            if not os.path.exists(REPORT_DIR):
                os.makedirs(REPORT_DIR)

            # Genera il file nel formato selezionato
            file_name_base = f"rapport_{report_type}_{today.strftime('%d-%m-%Y')}"
            if export_format == "pdf":
                file_name = os.path.join(REPORT_DIR, f"{file_name_base}.pdf") # Usa REPORT_DIR
                self.generate_pdf_report(file_name, report_data)
            elif export_format == "csv":
                file_name = os.path.join(REPORT_DIR, f"{file_name_base}.csv") # Usa REPORT_DIR
                self.generate_csv_report(file_name, report_data)
            elif export_format == "xlsx":
                file_name = os.path.join(REPORT_DIR, f"{file_name_base}.xlsx") # Usa REPORT_DIR
                self.generate_xlsx_report(file_name, report_data)
            else:
                QMessageBox.warning(self, "Erreur", f"Format d'exportation non supporté: {export_format}")
                return
            # Mostra messaggio di successo
            reply = QMessageBox.question(
                self,
                "Succès",
                f"Le rapport {report_type} a été exporté en {export_format.upper()} : {file_name}\nVoulez-vous l'ouvrir maintenant ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(file_name)))
                except Exception as open_error:
                    QMessageBox.warning(self, "Erreur Ouverture", f"Impossible d'ouvrir le fichier: {open_error}")
        except Exception as e:
            logging.error(f"Erreur lors de la génération du rapport : {str(e)}")
            QMessageBox.critical(self, "Erreur Rapport", f"Erreur lors de la génération du rapport : {str(e)}")

    def generate_pdf_report(self, file_name, report_data):
        """Genera il rapporto in formato PDF."""
        try:
            doc = SimpleDocTemplate(file_name, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Titolo del rapporto
            title = Paragraph(report_data['title'], styles["Title"])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Riepilogo finanziario
            summary_data = [
                ["Total des ventes", f"{report_data['total_sales']:.2f} CFA"],
                ["Coût total des articles vendus", f"{report_data['total_purchase_cost']:.2f} CFA"],
                ["Total des dépenses", f"{report_data['total_expenses']:.2f} CFA"],
                ["Bénéfice net", f"{report_data['net_profit']:.2f} CFA"],
            ]
            summary_table = Table(summary_data, colWidths=[250, 150])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 24))

            # Dettagli delle vendite
            if report_data['sales_details']:
                elements.append(Paragraph("Détails des ventes :", styles["Heading2"]))
                sales_table_data = [["Article", "Quantité vendue", "Montant total", "Date de vente", "Client"]] + report_data['sales_details']
                sales_table = Table(sales_table_data, colWidths=[120, 100, 100, 100, 120])
                sales_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))
                elements.append(sales_table)
                elements.append(Spacer(1, 24))

            # Elenco dei clienti unici
            if report_data['unique_customers']:
                elements.append(Paragraph("Clients ayant effectué des achats :", styles["Heading2"]))
                customers_table_data = [["Nom du client"]] + [[customer] for customer in report_data['unique_customers']]
                customers_table = Table(customers_table_data, colWidths=[400])
                customers_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))
                elements.append(customers_table)
                elements.append(Spacer(1, 24))

            # Ordini d'acquisto
            if report_data['purchase_orders']:
                elements.append(Paragraph("Ordres d'Achat :", styles["Heading2"]))
                purchase_orders_data = [["ID", "Fournisseur", "Date de Commande", "Date de Livraison", "Statut"]] + report_data['purchase_orders']
                purchase_orders_table = Table(purchase_orders_data, colWidths=[50, 150, 100, 100, 100])
                purchase_orders_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))
                elements.append(purchase_orders_table)
                elements.append(Spacer(1, 24))

            # Dettagli delle righe degli ordini d'acquisto
            if report_data['purchase_order_items']:
                elements.append(Paragraph("Détails des Ordres d'Achat :", styles["Heading2"]))
                for order_id, items in report_data['purchase_order_items'].items():
                    elements.append(Paragraph(f"Ordre ID: {order_id}", styles["Heading3"]))
                    order_items_data = [["Article", "Quantité", "Montant Total (CFA)"]] + items
                    order_items_table = Table(order_items_data, colWidths=[150, 100, 150])
                    order_items_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ]))
                    elements.append(order_items_table)
                    elements.append(Spacer(1, 12))

            # Fornitori coinvolti
            if report_data['suppliers_involved']:
                elements.append(Paragraph("Fournisseurs impliqués :", styles["Heading2"]))
                suppliers_table_data = [["Nom du Fournisseur"]] + [[supplier] for supplier in report_data['suppliers_involved']]
                suppliers_table = Table(suppliers_table_data, colWidths=[400])
                suppliers_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))
                elements.append(suppliers_table)

            # Costruisci il PDF
            doc.build(elements)

        except Exception as e:
            raise Exception(f"Erreur lors de la génération du PDF: {str(e)}")

    def generate_csv_report(self, file_name, report_data):
        """Genera il rapporto in formato CSV."""
        try:
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Titolo e Riepilogo
                writer.writerow([report_data['title']])
                writer.writerow([]) # Riga vuota
                writer.writerow(["Riepilogo Finanziario"])
                writer.writerow(["Description", "Valeur"])
                writer.writerow(["Total des ventes", f"{report_data['total_sales']:.2f} CFA"])
                writer.writerow(["Coût total des articles vendus", f"{report_data['total_purchase_cost']:.2f} CFA"])
                writer.writerow(["Total des dépenses", f"{report_data['total_expenses']:.2f} CFA"])
                writer.writerow(["Bénéfice net", f"{report_data['net_profit']:.2f} CFA"])
                writer.writerow([]) # Riga vuota

                # Dettagli Vendite
                if report_data['sales_details']:
                    writer.writerow(["Détails des ventes"])
                    writer.writerow(["Article", "Quantité vendue", "Montant total", "Date de vente", "Client"])
                    writer.writerows(report_data['sales_details'])
                    writer.writerow([]) # Riga vuota

                # Clienti Unici
                if report_data['unique_customers']:
                    writer.writerow(["Clients ayant effectué des achats"])
                    writer.writerow(["Nom du client"])
                    for customer in report_data['unique_customers']:
                        writer.writerow([customer])
                    writer.writerow([]) # Riga vuota

                # Ordini d'Acquisto
                if report_data['purchase_orders']:
                    writer.writerow(["Ordres d'Achat"])
                    writer.writerow(["ID", "Fournisseur", "Date de Commande", "Date de Livraison", "Statut"])
                    writer.writerows(report_data['purchase_orders'])
                    writer.writerow([]) # Riga vuota

                # Dettagli Ordini d'Acquisto
                if report_data['purchase_order_items']:
                    writer.writerow(["Détails des Ordres d'Achat"])
                    for order_id, items in report_data['purchase_order_items'].items():
                        writer.writerow([f"Ordre ID: {order_id}"])
                        writer.writerow(["Article", "Quantité", "Montant Total (CFA)"])
                        writer.writerows(items)
                        writer.writerow([]) # Riga vuota

                # Fornitori Coinvolti
                if report_data['suppliers_involved']:
                    writer.writerow(["Fournisseurs impliqués"])
                    writer.writerow(["Nom du Fournisseur"])
                    for supplier in report_data['suppliers_involved']:
                        writer.writerow([supplier])

        except Exception as e:
            raise Exception(f"Erreur lors de la génération du CSV: {str(e)}")

    def create_manual_backup(self):
        """Trigger la creazione di un backup manuale."""
        try:
            # Importa la funzione solo quando serve
            from utils.backup_manager import create_backup
            backup_path = create_backup()
            if backup_path:
                QMessageBox.information(self, "Succès", f"Backup manuel créé avec succès:\n{os.path.basename(backup_path)}")
                # Opzionale: chiedere se aprire la directory
                reply = QMessageBox.question(self, "Ouvrir Dossier", "Voulez-vous ouvrir le dossier des backups ?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    from utils.backup_manager import open_backup_directory
                    open_backup_directory()
            else:
                 QMessageBox.warning(self, "Échec", "La création du backup manuel a échoué.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Backup", f"Erreur lors de la création du backup manuel : {str(e)}")

    def request_password_for_restore(self):
        """Richiede la password prima di avviare il ripristino."""
        if not hasattr(self.parent_window, 'password'):
            QMessageBox.critical(self, "Erreur", "La variable 'password' n'est pas définie dans la classe principale.")
            return False

        password, ok = QInputDialog.getText(
            self,
            "Authentification",
            "Entrez le mot de passe pour restaurer le backup :",
            QLineEdit.Password
        )
        if ok and password == self.parent_window.password:
            self.restore_from_backup()
        elif ok:
            QMessageBox.warning(self, "Erreur", "Mot de passe incorrect !")

    def restore_from_backup(self):
        """Avvia il processo di ripristino."""
        from utils.backup_manager import select_backup_file, restore_backup
        backup_file = select_backup_file(self)
        if backup_file:
            restore_backup(backup_file)

    def generate_xlsx_report(self, file_name, report_data):
        """Genera il rapporto in formato XLSX."""
        try:
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                # Riepilogo
                summary_df = pd.DataFrame([
                    {"Description": "Total des ventes", "Valeur": f"{report_data['total_sales']:.2f} CFA"},
                    {"Description": "Coût total des articles vendus", "Valeur": f"{report_data['total_purchase_cost']:.2f} CFA"},
                    {"Description": "Total des dépenses", "Valeur": f"{report_data['total_expenses']:.2f} CFA"},
                    {"Description": "Bénéfice net", "Valeur": f"{report_data['net_profit']:.2f} CFA"}
                ])
                summary_df.to_excel(writer, sheet_name='Riepilogo', index=False)

                # Dettagli Vendite
                if report_data['sales_details']:
                    sales_df = pd.DataFrame(report_data['sales_details'], columns=["Article", "Quantité vendue", "Montant total", "Date de vente", "Client"])
                    sales_df.to_excel(writer, sheet_name='Dettagli Vendite', index=False)

                # Clienti Unici
                if report_data['unique_customers']:
                    customers_df = pd.DataFrame(report_data['unique_customers'], columns=["Nom du client"])
                    customers_df.to_excel(writer, sheet_name='Clienti Unici', index=False)

                # Ordini d'Acquisto
                if report_data['purchase_orders']:
                    po_df = pd.DataFrame(report_data['purchase_orders'], columns=["ID", "Fournisseur", "Date de Commande", "Date de Livraison", "Statut"])
                    po_df.to_excel(writer, sheet_name='Ordini Acquisto', index=False)

                # Dettagli Ordini d'Acquisto
                if report_data['purchase_order_items']:
                    all_items = []
                    for order_id, items in report_data['purchase_order_items'].items():
                        for item in items:
                            all_items.append([order_id] + list(item))
                    po_items_df = pd.DataFrame(all_items, columns=["ID Ordine", "Article", "Quantité", "Montant Total (CFA)"])
                    po_items_df.to_excel(writer, sheet_name='Dettagli Ordini Acquisto', index=False)

                # Fornitori Coinvolti
                if report_data['suppliers_involved']:
                    suppliers_df = pd.DataFrame(report_data['suppliers_involved'], columns=["Nom du Fournisseur"])
                    suppliers_df.to_excel(writer, sheet_name='Fornitori Coinvolti', index=False)

        except ImportError:
            QMessageBox.critical(self, "Erreur Export XLSX", "La libreria 'openpyxl' è necessaria per esportare in XLSX. Installala con 'pip install openpyxl'.")
            raise Exception("La libreria 'openpyxl' non è installata. Impossibile esportare in XLSX.")
        except Exception as e:
            raise Exception(f"Erreur lors de la génération du XLSX: {str(e)}")
