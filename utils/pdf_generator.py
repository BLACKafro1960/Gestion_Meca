from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(file_name, content):
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Titolo del rapporto
    title = Paragraph(content['title'], styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Riepilogo finanziario
    summary_data = [
        ["Total des ventes", f"{content['total_sales']:.2f} CFA"],
        ["Coût total des articles vendus", f"{content['total_purchase_cost']:.2f} CFA"],
        ["Total des dépenses", f"{content['total_expenses']:.2f} CFA"],
        ["Bénéfice net", f"{content['net_profit']:.2f} CFA"],
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
    if content['sales_details']:
        elements.append(Paragraph("Détails des ventes :", styles["Heading2"]))
        sales_table_data = [["Article", "Quantité vendue", "Montant total", "Date de vente", "Client"]] + content['sales_details']
        sales_table = Table(sales_table_data, colWidths=[120, 100, 100, 100, 120])
        sales_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(sales_table)
        elements.append(Spacer(1, 24))

    # Elenco dei clienti unici
    if content['unique_customers']:
        elements.append(Paragraph("Clients ayant effectué des achats :", styles["Heading2"]))
        customers_table_data = [["Nom du client"]] + [[customer] for customer in content['unique_customers']]
        customers_table = Table(customers_table_data, colWidths=[400])
        customers_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(customers_table)
        elements.append(Spacer(1, 24))

    # Ordini d'acquisto
    if content['purchase_orders']:
        elements.append(Paragraph("Ordres d'Achat :", styles["Heading2"]))
        purchase_orders_data = [["ID", "Fournisseur", "Date de Commande", "Date de Livraison", "Statut"]] + content['purchase_orders']
        purchase_orders_table = Table(purchase_orders_data, colWidths=[50, 150, 100, 100, 100])
        purchase_orders_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(purchase_orders_table)
        elements.append(Spacer(1, 24))

    # Dettagli delle righe degli ordini d'acquisto
    if content['purchase_order_items']:
        elements.append(Paragraph("Détails des Ordres d'Achat :", styles["Heading2"]))
        for order_id, items in content['purchase_order_items'].items():
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
    if content['suppliers_involved']:
        elements.append(Paragraph("Fournisseurs impliqués :", styles["Heading2"]))
        suppliers_table_data = [["Nom du Fournisseur"]] + [[supplier] for supplier in content['suppliers_involved']]
        suppliers_table = Table(suppliers_table_data, colWidths=[400])
        suppliers_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        elements.append(suppliers_table)

    # Costruisci il PDF
    doc.build(elements)
