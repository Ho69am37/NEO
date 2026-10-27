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
        self.symbols.clear()

    def insert(self, name, symbol_type):
        """
        Insert a new symbol into the table.

        A variable cannot be declared more than once.

        Raises:
            SemanticError: if the variable has already been declared.
        """
        if name not in self.symbols:
            self.symbols[name] = symbol_type
        else:
            raise SemanticError(f"the variable '{name}' has already been declared.")    

    def lookup(self, name):
        """
        Look up a symbol in the table.

        Raises:
            SemanticError: if the variable has not been declared.

        Returns:
            The information associated with the symbol.
        """
        if name not in self.symbols:
            raise SemanticError(f"The variable '{name}' has not been declared.")
        return self.symbols[name]