import logging
from datetime import datetime
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from ..config import *

class NotificationManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.tray_icon = None
        self.notification_queue = []
        self.setup_tray_icon()

    def setup_tray_icon(self):
        """Configura l'icona nella system tray"""
        try:
            self.tray_icon = QSystemTrayIcon(self.parent)
            self.tray_icon.setIcon(QIcon('resources/icons/app_icon.png'))
            
            # Menu contestuale
            tray_menu = QMenu()
            tray_menu.addAction('Mostra/Nascondi', self.parent.show)
            tray_menu.addSeparator()
            tray_menu.addAction('Esci', self.parent.close)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
        except Exception as e:
            logging.error(f'Errore durante la configurazione della system tray: {str(e)}')

    def check_low_stock(self):
        """Controlla gli articoli con stock basso"""
        try:
            from ..database import fetch_all
            low_stock_items = fetch_all(
                "SELECT article_name, quantity FROM articles WHERE quantity < ?",
                (LOW_STOCK_THRESHOLD,)
            )

            if low_stock_items:
                message = "Articoli con stock basso:\n\n"
                for item_name, quantity in low_stock_items:
                    message += f"- {item_name}: {quantity} unità\n"
                    
                self.show_notification(
                    "Avviso Stock Basso",
                    message,
                    QSystemTrayIcon.Warning
                )
                
                # Registra l'avviso nel log
                logging.warning(f'Rilevati {len(low_stock_items)} articoli con stock basso')
                
        except Exception as e:
            logging.error(f'Errore durante il controllo dello stock: {str(e)}')

    def show_notification(self, title, message, icon_type=QSystemTrayIcon.Information):
        """Mostra una notifica di sistema"""
        try:
            if self.tray_icon and self.tray_icon.supportsMessages():
                self.tray_icon.showMessage(
                    title,
                    message,
                    icon_type,
                    5000  # Durata in millisecondi
                )
                
                # Registra la notifica nel log
                logging.info(f'Notifica mostrata: {title} - {message}')
        except Exception as e:
            logging.error(f'Errore durante la visualizzazione della notifica: {str(e)}')

    def schedule_stock_check(self, interval=3600):
        """Programma il controllo periodico dello stock"""
        try:
            timer = QTimer(self.parent)
            timer.timeout.connect(self.check_low_stock)
            timer.start(interval * 1000)  # Converti in millisecondi
            logging.info(f'Controllo stock programmato ogni {interval} secondi')
        except Exception as e:
            logging.error(f'Errore durante la programmazione del controllo stock: {str(e)}')

    def notify_backup_status(self, success):
        """Notifica lo stato del backup"""
        if success:
            self.show_notification(
                "Backup Completato",
                "Il backup del database è stato completato con successo.",
                QSystemTrayIcon.Information
            )
        else:
            self.show_notification(
                "Errore Backup",
                "Si è verificato un errore durante il backup del database.",
                QSystemTrayIcon.Critical
            )

    def notify_order_status(self, order_id, status):
        """Notifica il cambio di stato di un ordine"""
        self.show_notification(
            "Aggiornamento Ordine",
            f"L'ordine #{order_id} è stato aggiornato a: {status}",
            QSystemTrayIcon.Information
        )