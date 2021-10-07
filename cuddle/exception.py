class KDLDecodeError(ValueError):
    pass


class KDLEncodeTypeError(TypeError):
    pass


__all__ = (
    "KDLDecodeError",
    "KDLEncodeTypeError",
)
