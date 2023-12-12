import os
from prompt_toolkit.validation import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message="Please enter a number", cursor_position=len(document.text)
            )


class PathValidator(Validator):
    def validate(self, document):
        if not os.path.exists(document.text) or not document.text.endswith(".csv"):
            raise ValidationError(
                message="Path is not a valid csv file",
                cursor_position=len(document.text),
            )
