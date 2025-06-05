import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from ..config import PASSWORD_SALT, SESSION_TIMEOUT

class SecurityManager:
    def __init__(self):
        self.sessions = {}

    def hash_password(self, password):
        """Genera un hash sicuro della password"""
        try:
            # Combina la password con il salt
            salted = password + PASSWORD_SALT
            # Genera l'hash usando SHA-256
            hashed = hashlib.sha256(salted.encode()).hexdigest()
            return hashed
        except Exception as e:
            logging.error(f'Errore durante l\'hashing della password: {str(e)}')
            return None

    def verify_password(self, password, hashed_password):
        """Verifica se la password corrisponde all'hash memorizzato"""
        try:
            return self.hash_password(password) == hashed_password
        except Exception as e:
            logging.error(f'Errore durante la verifica della password: {str(e)}')
            return False

    def create_session(self, user_id):
        """Crea una nuova sessione per l'utente"""
        try:
            session_token = secrets.token_hex(32)
            self.sessions[session_token] = {
                'user_id': user_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            return session_token
        except Exception as e:
            logging.error(f'Errore durante la creazione della sessione: {str(e)}')
            return None

    def validate_session(self, session_token):
        """Verifica se una sessione è valida e non è scaduta"""
        try:
            if session_token not in self.sessions:
                return False

            session = self.sessions[session_token]
            now = datetime.now()

            # Verifica se la sessione è scaduta
            if (now - session['last_activity']).total_seconds() > SESSION_TIMEOUT:
                self.invalidate_session(session_token)
                return False

            # Aggiorna il timestamp dell'ultima attività
            session['last_activity'] = now
            return True
        except Exception as e:
            logging.error(f'Errore durante la validazione della sessione: {str(e)}')
            return False

    def invalidate_session(self, session_token):
        """Invalida una sessione esistente"""
        try:
            if session_token in self.sessions:
                del self.sessions[session_token]
                return True
            return False
        except Exception as e:
            logging.error(f'Errore durante l\'invalidazione della sessione: {str(e)}')
            return False

    def cleanup_expired_sessions(self):
        """Rimuove tutte le sessioni scadute"""
        try:
            now = datetime.now()
            expired_tokens = [
                token for token, session in self.sessions.items()
                if (now - session['last_activity']).total_seconds() > SESSION_TIMEOUT
            ]
            for token in expired_tokens:
                self.invalidate_session(token)
            return len(expired_tokens)
        except Exception as e:
            logging.error(f'Errore durante la pulizia delle sessioni: {str(e)}')
            return 0

    def generate_temporary_password(self, length=12):
        """Genera una password temporanea sicura"""
        try:
            # Caratteri per la password
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
            # Genera la password
            password = ''.join(secrets.choice(chars) for _ in range(length))
            return password
        except Exception as e:
            logging.error(f'Errore durante la generazione della password temporanea: {str(e)}')
            return None