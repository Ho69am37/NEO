class SemanticError(Exception):
    """
    Exception raised when a semantic error is detected
    in a Neo program.
    """
    pass

class FunctionSymbol:
    def __init__(self, name, return_type, param_types):
        self.kind = "function"
        self.name = name
        self.return_type = return_type   # void - bool - int
        self.param_types = param_types   #int - bool

    def __repr__(self):
        return f"{self.return_type} {self.name}({', '.join(self.param_types)})"    

    
class SymbolTable:
    """
    Symbol table for the Neo language.

    In Neo P3 there is a single global scope.
    Each symbol stores its name and type.
    """

    def __init__(self):
        self.scopes = [{}]

    def clear(self):
        self.scopes = [{}]

    #------ scope management ------
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def depth_scope(self):
        return len(self.scopes)

    #---- variables ----
    def insert(self, name, symbol_type):
        """
        Insert a new symbol into the table.

        A variable cannot be declared more than once.

        Raises:
            SemanticError: if the variable has already been declared.
        """
        current = self.scopes[-1]
        if name in current:
            raise SemanticError(f"The name {name} has already been declared in this scope.")
        current[name] = symbol_type

    def lookup(self, name):
        
        for scope in reversed(self.scopes):
            if name in scope:
                entry = scope[name]
                if isinstance(entry, FunctionSymbol):
                    raise SemanticError(
                        f"'{name}' is a function, not a variable."
                    )
                return entry
        raise SemanticError(f"The variable '{name}' has not been declared.")

    #---- Functions ----
    def insert_function(self, name,  return_type, param_types):
        """ insert the function in the global scope """
        global_scope = self.scopes[0]
        if name in global_scope:
            raise SemanticError(f"The function '{name}' has already been defined.")
        symbol = FunctionSymbol(name,  return_type, param_types)
        global_scope[name] = symbol
        return symbol

    def lookup_function(self, name):
        entry = self.scopes[0].get(name)
        if not isinstance(entry, FunctionSymbol):
            raise SemanticError(f"The function '{name}' has not been defined.")
        return entry