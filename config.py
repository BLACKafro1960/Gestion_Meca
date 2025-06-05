import os

# Configurazione del database
DATABASE_PATH = "gestion_meca.db"

# Configurazione del backup
BACKUP_DIR = "backups"
BACKUP_INTERVAL = 24 * 60 * 60  # 24 ore in secondi
MAX_BACKUPS = 7  # Numero massimo di backup da mantenere

# Configurazione delle immagini dei prodotti
IMAGES_DIR = "product_images"
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
THUMBNAIL_SIZE = (200, 200)  # Dimensioni delle miniature (larghezza, altezza)

# Configurazione della sicurezza
PASSWORD_SALT = "gestion_meca_salt"  # Salt per l'hashing delle password
SESSION_TIMEOUT = 30 * 60  # 30 minuti in secondi

# Configurazione delle notifiche
LOW_STOCK_THRESHOLD = 5  # Soglia per le notifiche di stock basso
NOTIFICATION_SOUND = True  # Abilita/disabilita i suoni delle notifiche

# Configurazione dei report
REPORT_DIR = "reports"
DEFAULT_REPORT_FORMAT = "pdf"
AVAILABLE_REPORT_FORMATS = ["pdf", "csv", "xlsx"]

# Assicura che le directory necessarie esistano
def ensure_directories():
    directories = [BACKUP_DIR, IMAGES_DIR, REPORT_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)