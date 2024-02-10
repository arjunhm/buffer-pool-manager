class PageNotFoundError(Exception):
    def __init__(self, message, errors):
        message = "Page not found"
        super().__init__(message)

