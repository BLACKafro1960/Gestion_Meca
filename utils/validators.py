from PySide6.QtGui import QValidator

class PositiveIntValidator(QValidator):
    def validate(self, input_text, pos):
        if input_text.isdigit() and int(input_text) > 0:
            return QValidator.Acceptable
        elif input_text == "" or input_text == "-":
            return QValidator.Intermediate
        else:
            return QValidator.Invalid

class PositiveFloatValidator(QValidator):
    def validate(self, input_text, pos):
        try:
            value = float(input_text)
            if value > 0:
                return QValidator.Acceptable
            else:
                return QValidator.Invalid
        except ValueError:
            if input_text == "" or input_text == "." or input_text == "-":
                return QValidator.Intermediate
            else:
                return QValidator.Invalid
