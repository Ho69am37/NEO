NEO - PRACTICE 4 UPDATE
Boolean Expressions, Sensors and Type Checking
================================================

This package contains the files required to update your Neo project
from Practice 3 to Practice 4.

IMPORTANT
---------
Do not replace your complete project with this folder.

You must continue working with the compiler developed during the
previous practices.

The following files are provided in this update:

    neo.py
    compiler/__init__.py
    compiler/ast_nodes.py
    compiler/evaluator.py

Copy these files into your existing Neo project, replacing the
previous versions when necessary.

Your existing files:

    compiler/lexer.py
    compiler/parser.py
    compiler/symbol_table.py

must be preserved and extended according to the Practice 4 statement.


WHAT IS NEW IN THIS UPDATE?
---------------------------

Practice 4 introduces Boolean expressions and interaction with
the Neo world through sensors.

The AST has therefore been extended with new node types and with
semantic type information for expressions.

Expression nodes contain a 'type' attribute. This attribute is
intended to store the type determined during syntax-directed
semantic analysis.

The evaluator has also been extended to support Boolean values,
Boolean operations and the Neo sensors.

The graphical environment provides the runtime implementation of
the sensors used in this practice.


HOW TO UPDATE YOUR PROJECT
--------------------------

1. Start from your working Practice 3 project.

2. Copy neo.py from this package into your project.

3. Copy the files contained in the compiler directory into the
   compiler directory of your project.

4. Keep your existing lexer.py, parser.py and symbol_table.py.

5. Extend your compiler according to the Practice 4 statement.

6. Run Neo with:

       python neo.py


IMPORTANT
---------
The files provided in this package implement the infrastructure
required by the Neo environment.

The lexical, syntactic and syntax-directed semantic analysis
required in Practice 4 must be implemented by you.

Do not modify the provided infrastructure unless explicitly
instructed to do so.
