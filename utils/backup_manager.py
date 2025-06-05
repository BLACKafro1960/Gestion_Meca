import os
import shutil
import time
from datetime import datetime
import sqlite3
from PIL import Image
import logging
from config import DATABASE_PATH, BACKUP_DIR, MAX_BACKUPS, IMAGES_DIR, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE, THUMBNAIL_SIZE

class BackupManager:
    @staticmethod
    def create_backup():
        """Crea un backup del database"""
        try:
            # Assicura che la directory dei backup esista
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)

            # Crea il nome del file di backup con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.db')

            # Copia il database
            shutil.copy2(DATABASE_PATH, backup_file)

            # Rimuovi i backup più vecchi se necessario
            BackupManager._cleanup_old_backups()

            logging.info(f'Backup creato con successo: {backup_file}')
            return True
        except Exception as e:
            logging.error(f'Errore durante la creazione del backup: {str(e)}')
            return False

    @staticmethod
    def _cleanup_old_backups():
        """Rimuove i backup più vecchi se si supera il numero massimo consentito"""
        try:
            backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_') and f.endswith('.db')]
            backups.sort(reverse=True)

            # Rimuovi i backup in eccesso
            while len(backups) > MAX_BACKUPS:
                old_backup = os.path.join(BACKUP_DIR, backups.pop())
                os.remove(old_backup)
                logging.info(f'Backup rimosso: {old_backup}')
        except Exception as e:
            logging.error(f'Errore durante la pulizia dei backup: {str(e)}')

class ImageManager:
    @staticmethod
    def save_product_image(image_path, product_id):
        """Salva l'immagine di un prodotto e crea una miniatura"""
        try:
            # Verifica l'estensione del file
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValueError(f'Formato file non supportato. Formati consentiti: {ALLOWED_IMAGE_EXTENSIONS}')

            # Verifica la dimensione del file
            if os.path.getsize(image_path) > MAX_IMAGE_SIZE:
                raise ValueError(f'Immagine troppo grande. Dimensione massima: {MAX_IMAGE_SIZE/1024/1024}MB')

            # Crea le directory se non esistono
            product_dir = os.path.join(IMAGES_DIR, str(product_id))
            if not os.path.exists(product_dir):
                os.makedirs(product_dir)

            # Salva l'immagine originale
            dest_path = os.path.join(product_dir, f'original{ext}')
            shutil.copy2(image_path, dest_path)

            # Crea e salva la miniatura
            thumb_path = os.path.join(product_dir, f'thumbnail{ext}')
            ImageManager._create_thumbnail(image_path, thumb_path)

            logging.info(f'Immagine salvata con successo per il prodotto {product_id}')
            return True
        except Exception as e:
            logging.error(f'Errore durante il salvataggio dell\'immagine: {str(e)}')
            return False

    @staticmethod
    def _create_thumbnail(source_path, thumb_path):
        """Crea una miniatura dell'immagine"""
        try:
            with Image.open(source_path) as img:
                img.thumbnail(THUMBNAIL_SIZE)
                img.save(thumb_path)
        except Exception as e:
            logging.error(f'Errore durante la creazione della miniatura: {str(e)}')
            raise

    @staticmethod
    def delete_product_images(product_id):
        """Elimina tutte le immagini associate a un prodotto"""
        try:
            product_dir = os.path.join(IMAGES_DIR, str(product_id))
            if os.path.exists(product_dir):
                shutil.rmtree(product_dir)
                logging.info(f'Immagini eliminate per il prodotto {product_id}')
                return True
            return False
        except Exception as e:
            logging.error(f'Errore durante l\'eliminazione delle immagini: {str(e)}')
            return False