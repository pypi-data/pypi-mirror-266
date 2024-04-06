from mlflow.exceptions import MlflowException


class MlFoundryException(MlflowException):
    def __init__(self, message):
        super().__init__(message=message)
        self.message = message
