NEO P5 UPDATE
=============

This package contains the new infrastructure required for Neo Practice 5.

Practice 5 introduces control flow using if/else statements, while loops,
and blocks.

IMPORTANT
---------

Continue working on your own Neo project from Practice 4.

Do NOT replace your lexer.py, parser.py, symbol_table.py or evaluator.py
files with new versions. You must extend your existing compiler.

FILES INCLUDED
--------------

neo.py
    Updated Neo execution environment for Practice 5.

    Replace your current neo.py file with this version.

compiler/ast_nodes.py
    Updated AST definitions for Practice 5.

    Replace your current compiler/ast_nodes.py file with this version.

    The following AST nodes are introduced:

        Block
        If
        While

WHAT YOU MUST IMPLEMENT
-----------------------

1. Extend your existing compiler/lexer.py.

   Add the lexical elements required for:

       if
       else
       while
       {
       }

2. Extend your existing compiler/parser.py.

   Add the grammar rules required to recognize:

       if (condition) {
           ...
       }

       if (condition) {
           ...
       } else {
           ...
       }

       while (condition) {
           ...
       }

   Your parser must construct the corresponding Block, If and While
   AST nodes.

3. Extend the syntax-directed semantic analysis performed by your parser.

   The conditions of if and while statements must have type bool.

   If a condition has any other type, a SemanticError must be raised.

BLOCKS
------

A block must contain at least one executable statement.

Variable declarations are not allowed inside blocks in Practice 5.

Control-flow statements may be nested. Therefore, if and while statements
may appear inside other if and while blocks.

RUNTIME
-------

The updated neo.py file already implements the execution of the new
control-flow AST nodes.

You do not need to implement the runtime execution of if or while.

The condition of a while statement is evaluated again before every
iteration.

DO NOT MODIFY
-------------

The following files provided as infrastructure must not be modified:

    neo.py
    compiler/ast_nodes.py

Continue using your evaluator.py and symbol_table.py implementations
from Practice 4.
