from http import HTTPStatus


class CustomException(Exception):
    status_code = HTTPStatus.BAD_GATEWAY
    error_code = HTTPStatus.BAD_GATEWAY
    message = HTTPStatus.BAD_GATEWAY.description

    def __init__(self, message=None):
        if message:
            self.message = message

    def __str__(self) -> str:
        return str(self.error_code)

