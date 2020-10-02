

class PrimitiveNotSetException(Exception):
    """Exception raised for incorrect Context setup w.r.t. EDNA job primitives.

    """
    def __init__(self, context: str, primitive: str):
        """Raise PrimitiveNotSetException

        Args:
            context ([str]): Name of the EdnaContext class
            primitive ([str]): Name of the primitive
        """
        self.message = "Primitive {primitive} is not set for the context {context}".format(primitive=primitive, context=context)
        super().__init__(self.message)