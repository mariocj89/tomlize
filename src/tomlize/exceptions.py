class FailedToParseError(Exception):
    def __init__(self, filename, error):
        self.filename = filename
        self.error = error
        super().__init__(f"Failed to parse {filename}: {error!r}")
