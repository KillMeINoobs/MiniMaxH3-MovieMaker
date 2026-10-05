"""Stable, path-redacted errors. UI translates codes without changing semantics."""
class ContractError(ValueError):
    def __init__(self, code, message, *, stage="validate", retryable=False, details=None):
        self.code = code
        self.message = message
        self.stage = stage
        self.retryable = retryable
        self.details = dict(details or {})
        super().__init__(f"{code}: {message}")

    def to_dict(self):
        return {"code": self.code, "message": self.message, "stage": self.stage,
                "retryable": self.retryable, "details": dict(self.details)}


def fail(code, message, **kwargs):
    raise ContractError(code, message, **kwargs)
