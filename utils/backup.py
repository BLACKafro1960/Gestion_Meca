import os
import shutil
import time
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
import logging

# Assicurati che il percorso per importare config sia corretto
# Potrebbe essere necessario aggiungere il percorso del progetto a sys.path
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import DATABASE_PATH, BACKUP_DIR, MAX_BACKUPS

# Considera di spostare la logica di business pura in BackupManager
# e usare questo file per funzioni che interagiscono direttamente con l'UI (QMessageBox, QFileDialog).

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_backup_with_ui_feedback(parent_widget=None): # Rinominata per chiarezza e per accettare un parent
    """Crea un backup del database e fornisce feedback UI."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"gestion_meca_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # Qui potresti chiamare una funzione da BackupManager se la logica è lì
        # Esempio:
        # from .backup_manager import BackupManager
        # if BackupManager.create_backup(): # Supponendo che create_backup() in BackupManager faccia la copia e cleanup
        #     logging.info(f"Backup creato con successo: {backup_path}") # backup_path dovrebbe essere ritornato da BackupManager
        #     QMessageBox.information(parent_widget, "Backup Creato", f"Backup creato con successo:\n{backup_filename}")
        #     return backup_path # o True
        # else:
        #     QMessageBox.critical(parent_widget, "Errore Backup", "Errore durante la creazione del backup.")
        #     return None # o False
        shutil.copy2(DATABASE_PATH, backup_path)
        logging.info(f"Backup creato con successo: {backup_path}")
        cleanup_backups() # Pulisci i backup vecchi dopo averne creato uno nuovo
        QMessageBox.information(parent_widget, "Backup Creato", f"Backup creato con successo:\n{backup_filename}")
        return backup_path
    except FileNotFoundError:
        logging.error(f"Errore: Database non trovato a {DATABASE_PATH}")
        QMessageBox.critical(parent_widget, "Errore Backup", f"Database non trovato a {DATABASE_PATH}")
        return None
    except Exception as e:
        logging.error(f"Errore durante la creazione del backup: {e}")
        QMessageBox.critical(parent_widget, "Errore Backup", f"Errore durante la creazione del backup: {str(e)}")
        return None

def cleanup_backups(): # Questa logica è duplicata in BackupManager._cleanup_old_backups
    """Elimina i backup più vecchi mantenendo solo MAX_BACKUPS.
    CONSIDERA DI USARE BackupManager._cleanup_old_backups() invece.
    """
    if not os.path.exists(BACKUP_DIR):
        return

    backup_files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
    backup_files.sort(key=os.path.getmtime) # Dal più vecchio al più recente

    if len(backup_files) > MAX_BACKUPS:
        # Calcola quanti file eliminare
        num_to_delete = len(backup_files) - MAX_BACKUPS
        files_to_delete = backup_files[:num_to_delete]
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                logging.info(f"Backup vecchio eliminato: {file_path}")
            except Exception as e:
                logging.error(f"Errore durante l'eliminazione del backup {file_path}: {e}")

def restore_backup(backup_path):
    """Ripristina il database da un file di backup specificato."""
    if not os.path.exists(backup_path):
        logging.error(f"Errore: File di backup non trovato a {backup_path}")
        QMessageBox.critical(None, "Errore Ripristino", f"File di backup non trovato: {backup_path}")
        return False

    confirmation = QMessageBox.question(
        None,
        "Conferma Ripristino",
        f"Sei sicuro di voler ripristinare il database dal backup:\n{os.path.basename(backup_path)}?\n"
        "Questo sovrascriverà i dati attuali e non potrà essere annullato.",
        QMessageBox.Yes | QMessageBox.No
    )

    if confirmation == QMessageBox.No:
        return False

    try:
        # Chiudi tutte le connessioni al database principale prima di sovrascriverlo
        # Questo è cruciale per evitare errori di file in uso.
        # Poiché le connessioni sono gestite per singola operazione in database.py,
        # non c'è un modo diretto per chiuderle tutte qui.
        # Un approccio più robusto richiederebbe una classe di gestione connessioni singleton.
        # Per questa implementazione, assumiamo che non ci siano operazioni DB attive.
        # Se l'applicazione è multithreaded o ha connessioni a lunga durata, questo potrebbe fallire.

        # Rinomina il database corrente come precauzione (opzionale ma consigliato)
        if os.path.exists(DATABASE_PATH):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(DATABASE_PATH, f"{DATABASE_PATH}.before_restore_{timestamp}")
            logging.info(f"Rinominato database corrente in {DATABASE_PATH}.before_restore_{timestamp}")

        shutil.copy2(backup_path, DATABASE_PATH)
        logging.info(f"Database ripristinato con successo da {backup_path}")
        QMessageBox.information(None, "Ripristino Completato", "Il database è stato ripristinato con successo.\nRiavviare l'applicazione per applicare completamente le modifiche.")
        return True
    except Exception as e:
        logging.error(f"Errore durante il ripristino del database: {e}")
        QMessageBox.critical(None, "Errore Ripristino", f"Errore durante il ripristino del database: {str(e)}")
        # Potresti voler provare a ripristinare il file rinominato qui in caso di errore
        return False

def select_backup_file(parent=None):
    """Permette all'utente di selezionare un file di backup."""
    if not os.path.exists(BACKUP_DIR):
        QMessageBox.warning(parent, "Nessun Backup Trovato", f"La directory dei backup '{BACKUP_DIR}' non esiste.")
        return None

    options = QFileDialog.Options()
    # options |= QFileDialog.DontUseNativeDialog # Opzionale: usa il dialog di Qt invece di quello nativo

    # Filtra solo i file .db nella directory dei backup
    file_filter = "Database Backup Files (*.db)"

    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Seleziona File di Backup",
        BACKUP_DIR, # Directory iniziale
        file_filter,
        options=options
    )

    return file_path

def open_backup_directory():
    """Apre la directory dei backup nel file explorer del sistema."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR) # Crea la directory se non esiste

    try:
        # QDesktopServices.openUrl funziona su diverse piattaforme
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(BACKUP_DIR)))
        logging.info(f"Aperta directory backup: {os.path.abspath(BACKUP_DIR)}")
    except Exception as e:
        logging.error(f"Errore nell'aprire la directory dei backup: {e}")
        QMessageBox.critical(None, "Errore", f"Impossibile aprire la directory dei backup: {str(e)}")