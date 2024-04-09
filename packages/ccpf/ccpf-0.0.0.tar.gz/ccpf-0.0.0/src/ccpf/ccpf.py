import native


def validate(cpf: str) -> bool:
    return native.validate(cpf)


def generate() -> str:
    return native.generate()


def has_mask(cpf: str) -> bool:
    return native.has_mask(cpf)


def mask(cpf: str) -> str:
    return native.mask(cpf)


def unmask(cpf: str) -> str:
    return native.unmask(cpf)
