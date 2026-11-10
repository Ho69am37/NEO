NEO - PRACTICE 6 UPDATE
Functions, Parameters, Return and Scopes

This package updates your existing Neo project from Practice 5.

FILES PROVIDED
--------------
neo.py
    Updated Neo GUI/runtime integration for Practice 6.

compiler/ast_nodes.py
    Updated AST node definitions for functions, parameters,
    function calls and return statements.

compiler/evaluator.py
    Updated runtime support. It models activation records,
    nested scopes, function calls, parameter binding, return
    values and recursion.

FILES YOU MUST EXTEND YOURSELVES
--------------------------------
compiler/lexer.py
compiler/parser.py
compiler/symbol_table.py

Do NOT replace these files with a new compiler. Extend the
implementation that you developed in the previous practices.

YOUR TASK
---------
Extend Neo with:

1. Functions
   - Return types: int, bool and void.
   - Functions are defined at global level.
   - Nested function definitions are not allowed.

2. Parameters
   - Parameter types: int and bool.
   - Arguments must match the number and types of parameters.

3. main()
   - Every valid Neo P6 program must define:
         void main()
   - main() takes no parameters.
   - Executable top-level statements are no longer allowed.

4. return
   - Non-void functions use:
         return expression;
   - The expression type must match the declared return type.
   - void functions do not use return in Practice 6.
   - You are NOT required to prove statically that every
     execution path returns a value. The runtime detects a
     non-void function that finishes without returning.

5. Scopes
   - Global scope: function names.
   - Function scope: parameters and local variables.
   - Block scope: variables declared inside if/else/while blocks.
   - Shadowing in nested scopes is allowed.
   - Redeclaration in the same scope is an error.
   - Variables are visible only while their scope is active.

6. Function calls
   - A function may call itself recursively.
   - A function may call only functions that have already been
     declared, except for itself.
   - A void function call is a statement.
   - A non-void function call may be used in an expression.
   - A void function cannot be used as an expression.
   - In this practice, the result of a non-void function call
     cannot be discarded as a standalone statement.

IMPORTANT IMPLEMENTATION IDEA
-----------------------------
The semantic checks must continue to be implemented through
syntax-directed semantic actions during parsing.

Do not create a separate semantic-analysis pass.

For recursion, insert the function symbol into the global symbol
table before analysing its body.

RUNTIME MODEL
-------------
The supplied evaluator models the runtime concepts studied in
class:

    call stack
        -> activation record for each function call
            -> function scope
            -> nested block scopes

Each recursive call therefore receives its own activation record.

TEST YOUR COMPILER
------------------
At minimum, test:

- void function without parameters
- function with parameters
- int/bool function returning a value
- function call inside an expression
- recursive function
- incorrect number of arguments
- incorrect argument type
- incorrect return type
- variable used outside its scope
- shadowing in a nested block
- non-void function that reaches the end without return

Run:
    python -m py_compile neo.py compiler/*.py
    python neo.py
