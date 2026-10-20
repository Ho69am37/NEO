NEO P3 UPDATE
=============

This package contains the new infrastructure required for Neo Practice 3.

Practice 3 introduces semantic analysis using syntax-directed semantic
actions and a symbol table.

IMPORTANT
---------

Continue working on your own Neo project from Practice 2.

Do NOT replace your lexer.py or parser.py files with new versions.
You must extend your existing compiler.

FILES INCLUDED
--------------

neo.py
    Updated Neo execution environment for Practice 3.

    Replace your current neo.py file with this version.

compiler/symbol_table.py
    Skeleton of the symbol table required in Practice 3.

    Copy this file into your compiler directory and complete the
    methods marked with TODO.

WHAT YOU MUST IMPLEMENT
-----------------------

1. Complete compiler/symbol_table.py.

   Implement the operations required to:

   - clear the symbol table,
   - insert variable declarations,
   - detect duplicate declarations,
   - look up previously declared variables,
   - detect uses of undeclared variables.

2. Extend your existing compiler/parser.py.

   Add the semantic actions required to:

   - insert variables into the symbol table when they are declared,
   - verify that the left-hand side of an assignment has been declared,
   - verify that variables used in expressions have been declared.

   These checks must be performed during parsing using syntax-directed
   semantic actions.

3. Your parser must maintain a SymbolTable instance and provide a way
   to clear it before analysing a new Neo program.

LEXER
-----

No changes are required in compiler/lexer.py for Practice 3.

LANGUAGE
--------

Practice 3 does not introduce new Neo syntax.

All programs accepted syntactically in Practice 2 remain part of the
language, but they must now satisfy the semantic rules introduced in
Practice 3.

ERRORS
------

Semantic errors must raise SemanticError, defined in:

    compiler/symbol_table.py

The updated Neo environment distinguishes lexical, syntax, semantic,
and runtime errors.

DO NOT MODIFY
-------------

The following file is provided as infrastructure and must not be modified:

    neo.py

The structure and behaviour of the provided skeleton should be preserved.
Only the methods marked with TODO in symbol_table.py must be completed.
