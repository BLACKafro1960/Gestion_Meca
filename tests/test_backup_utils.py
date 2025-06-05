import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Aggiungi la directory principale del progetto al percorso di Python
# Questo permette di importare i moduli come 'config' e 'utils.backup'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import utils.backup # Importa il modulo da testare
# Non importiamo direttamente BACKUP_DIR da config qui,
# perché lo patcheremo all'interno di utils.backup per i test.

# Definisci una directory di backup di test
TEST_BACKUP_DIR_CONSTANT = "test_backup_dir_for_select_file"

class TestSelectBackupFile(unittest.TestCase):

    def setUp(self):
        # Crea un widget genitore fittizio per QMessageBox e QFileDialog
        self.mock_parent_widget = MagicMock()

    # Patch per le dipendenze esterne usate da select_backup_file
    @patch('utils.backup.QMessageBox')
    @patch('utils.backup.os.path.exists')
    # Patch la variabile BACKUP_DIR all'interno del modulo utils.backup
    @patch('utils.backup.BACKUP_DIR', TEST_BACKUP_DIR_CONSTANT)
    def test_select_backup_file_no_backup_dir(self, mock_os_exists, mock_qmessagebox):
        """
        Testa select_backup_file quando la directory dei backup non esiste.
        """
        mock_os_exists.return_value = False # Simula che BACKUP_DIR non esista

        result = utils.backup.select_backup_file(parent=self.mock_parent_widget)

        # Verifica che os.path.exists sia stato chiamato con la directory di backup di test
        mock_os_exists.assert_called_once_with(TEST_BACKUP_DIR_CONSTANT)
        # Verifica che QMessageBox.warning sia stato chiamato con i parametri corretti
        mock_qmessagebox.warning.assert_called_once_with(
            self.mock_parent_widget,
            "Nessun Backup Trovato",
            f"La directory dei backup '{TEST_BACKUP_DIR_CONSTANT}' non esiste."
        )
        # Verifica che la funzione restituisca None
        self.assertIsNone(result)

    @patch('utils.backup.QFileDialog')
    @patch('utils.backup.os.path.exists')
    @patch('utils.backup.BACKUP_DIR', TEST_BACKUP_DIR_CONSTANT)
    def test_select_backup_file_backup_dir_exists_user_cancels(self, mock_os_exists, mock_qfiledialog):
        """
        Testa select_backup_file quando la directory esiste ma l'utente annulla.
        """
        mock_os_exists.return_value = True # Simula che BACKUP_DIR esista
        # Simula che l'utente annulli la finestra di dialogo
        mock_qfiledialog.getOpenFileName.return_value = ("", "")

        result = utils.backup.select_backup_file(parent=self.mock_parent_widget)

        mock_os_exists.assert_called_once_with(TEST_BACKUP_DIR_CONSTANT)
        # Verifica che QFileDialog.Options sia stato istanziato
        mock_qfiledialog.Options.assert_called_once()
        # Verifica che QFileDialog.getOpenFileName sia stato chiamato
        mock_qfiledialog.getOpenFileName.assert_called_once_with(
            self.mock_parent_widget,
            "Seleziona File di Backup",
            TEST_BACKUP_DIR_CONSTANT,
            "Database Backup Files (*.db)",
            options=mock_qfiledialog.Options.return_value # Verifica che l'oggetto options sia passato
        )
        self.assertEqual(result, "") # getOpenFileName restituisce una stringa vuota se annullato

    @patch('utils.backup.QFileDialog')
    @patch('utils.backup.os.path.exists')
    @patch('utils.backup.BACKUP_DIR', TEST_BACKUP_DIR_CONSTANT)
    def test_select_backup_file_backup_dir_exists_user_selects_file(self, mock_os_exists, mock_qfiledialog):
        """
        Testa select_backup_file quando la directory esiste e l'utente seleziona un file.
        """
        mock_os_exists.return_value = True # Simula che BACKUP_DIR esista
        selected_file_path = os.path.join(TEST_BACKUP_DIR_CONSTANT, "backup_test.db")
        # Simula che l'utente selezioni un file
        mock_qfiledialog.getOpenFileName.return_value = (selected_file_path, "Database Backup Files (*.db)")

        result = utils.backup.select_backup_file(parent=self.mock_parent_widget)

        mock_os_exists.assert_called_once_with(TEST_BACKUP_DIR_CONSTANT)
        mock_qfiledialog.Options.assert_called_once()
        mock_qfiledialog.getOpenFileName.assert_called_with(
            self.mock_parent_widget, "Seleziona File di Backup", TEST_BACKUP_DIR_CONSTANT, "Database Backup Files (*.db)", options=unittest.mock.ANY)
        self.assertEqual(result, selected_file_path)

if __name__ == '__main__':
    unittest.main()