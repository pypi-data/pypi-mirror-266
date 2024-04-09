import ctypes

class SecretString:
    def __init__(self, data: bytes):
        self.data = ctypes.create_string_buffer(data)

    def expose_secret(self) -> str:
        return self.data.value.decode('utf-8')

    def __del__(self):
        if hasattr(self, 'data'):
            ctypes.memset(self.data, 0, len(self.data))

    def __str__(self):
        return "SecretString :: [REDACTED]"

    def __repr__(self):
        return "SecretString :: [REDACTED]"

