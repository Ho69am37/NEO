class SemanticError(Exception):
    """
    Exception raised when a semantic error is detected
    in a Neo program.
    """
    pass


class SymbolTable:
    """
    Symbol table for the Neo language.

    In Neo P3 there is a single global scope.
    Each symbol stores its name and type.
    """

    def __init__(self):
        self.symbols = {}

    def clear(self):
        """
        Remove all symbols from the table.
        """
        # TODO: Implement this method.
        pass

    def insert(self, name, symbol_type):
        """
        Insert a new symbol into the table.

        A variable cannot be declared more than once.

        Raises:
            SemanticError: if the variable has already been declared.
        """
        # TODO: Implement this method.
        pass

    def lookup(self, name):
        """
        Look up a symbol in the table.

        Raises:
            SemanticError: if the variable has not been declared.

        Returns:
            The information associated with the symbol.
        """
        # TODO: Implement this method.
        pass
