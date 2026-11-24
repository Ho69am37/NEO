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
        self.return_type = return_type   
        self.param_types = param_types   
        self.local_size = 0
        self.memory_layout = []

    def __repr__(self):
        return f"{self.return_type} {self.name}({', '.join(self.param_types)})"    

class VariableSymbol:
    def __init__(self, name, type, kind="variable", size=None, offset=None):
        self.name = name
        self.type = type        # "int" or "bool" (element type for arrays)
        self.kind = kind        # "variable" or "array"
        self.size = size        # number of elements, only for arrays
        self.offset = offset    
    
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
    def insert(self, name, symbol_type, kind="variable", size=None):
        current = self.scopes[-1]
        if name in current:
            raise SemanticError(f"The name {name} has already been declared in this scope.")
        symbol = VariableSymbol(name, symbol_type, kind, size)
        current[name] = symbol
        return symbol

    def lookup_symbol(self, name): 
        for scope in reversed(self.scopes):
            if name in scope:
                entry = scope[name]
                if isinstance(entry, FunctionSymbol):
                    raise SemanticError(
                        f"'{name}' is a function, not a variable."
                    )
                return entry
        raise SemanticError(f"The variable '{name}' has not been declared.")

    def lookup(self, name):
        entry = self.lookup_symbol(name)
        if entry.kind == "array":
            raise SemanticError(f"'{name}' is an array and cannot be used as a scalar value.")
        return entry.type

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