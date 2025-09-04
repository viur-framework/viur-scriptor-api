from viur.scriptor._utils import is_pyodide_context

if not is_pyodide_context():
    from prompt_toolkit.validation import Validator, ValidationError
    import os

    class _ConvertableValidator(Validator):
        def __init__(self, conversion_function, error_message=None):
            super().__init__()
            self._conversion_function = conversion_function
            self._errormessage = error_message

        def validate(self, document):
            text = document.text
            try:
                self._conversion_function(text)
            except Exception:
                if self._errormessage is None:
                    errormessage = "The format is not correct."
                else:
                    errormessage = self._errormessage
                raise ValidationError(message=errormessage)

    class _StringNotEmptyValidator(Validator):
        def validate(self, document):
            if not document.text:
                raise ValidationError(message="You need to enter text. An empty string is not allowed.")


    class _FileDoesntExistsOrShouldBeReplacedValidator(Validator):
        def validate(self, document):
            text = document.text
            if not text.strip():
                raise ValidationError(message="Please enter a filename.")
            if os.path.exists(text) and not text.endswith('!'):
                raise ValidationError(
                    message="This file already exists. If you want to replace it, add an exclamation-mark (!) at the end.")
