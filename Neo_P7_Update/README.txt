NEO - PRACTICE 7 UPDATE
Arrays and Memory Management

This package updates your existing Neo project from Practice 6.

HOW TO USE THIS PACKAGE
-----------------------
Copy these files into your existing Neo P6 project, replacing the
corresponding files when requested.

FILES PROVIDED
--------------
neo.py
    Updated Neo GUI/runtime integration for Practice 7.
    It can display the memory layout produced by your parser.

compiler/ast_nodes.py
    Updated AST node definitions for one-dimensional arrays:
        ArrayDeclaration
        ArrayAssignment
        ArrayAccess

compiler/evaluator.py
    Updated runtime support for int and bool arrays.
    It allocates arrays, evaluates indexed accesses and assignments,
    and performs runtime bounds checking.

FILES YOU MUST EXTEND YOURSELVES
--------------------------------
compiler/lexer.py
compiler/parser.py
compiler/symbol_table.py

Do NOT replace these files with a new compiler. Extend the
implementation that you developed in the previous practices.

YOUR TASK
---------
Extend Neo P6 with static one-dimensional arrays and memory-layout
information.

1. Arrays
   Neo P7 supports arrays of int and bool:

       int values[5];
       bool visited[3];

   Arrays have a fixed positive size known at compile time.
   Arrays of arrays, matrices, dynamic arrays and array parameters
   are not part of Practice 7.

2. Array access
   An array element may be used in an expression:

       move(values[i]);
       if (visited[i]) {
           turn(LEFT);
       }

3. Array assignment
   An array element may be assigned a value:

       values[i] = 3;
       visited[i] = true;

4. Semantic checks
   Your syntax-directed semantic actions must check at least:

   - the declared array size is positive;
   - an indexed identifier is an array;
   - the array index has type int;
   - the assigned expression has the array element type;
   - arrays and scalar variables are not used interchangeably.

   As in previous practices, semantic checks are performed during
   parsing. Do not create a separate semantic-analysis pass.

5. Runtime bounds checking
   The supplied evaluator checks array bounds during execution.
   For an array of size N, valid indices are 0 ... N-1.

6. Storage model
   For Practice 7 use the following simplified storage sizes:

       int   = 4 bytes
       bool  = 4 bytes

   Array elements are stored contiguously.

7. Function memory layout
   Extend your compiler so that each function records the storage
   required by its parameters and local declarations.

   Use the following convention:

       EBP + 8     first parameter
       EBP + 12    second parameter
       ...
       EBP          previous EBP
       EBP - 4      local storage
       EBP - 8      local storage
       ...

   Parameters therefore use positive offsets and local variables use
   negative offsets.

   Every local declaration receives its own storage, including
   declarations inside nested blocks. Storage is not reused in this
   practice.

8. Array layout
   An array occupies one contiguous block. Store as its offset the
   address of element 0 (the lowest address in its reserved block).

   Example:

       int x;
       int values[3];

   may produce:

       x          offset -4     size 4
       values     offset -16    size 12

   Therefore:

       values[0]  -> EBP - 16
       values[1]  -> EBP - 12
       values[2]  -> EBP - 8

   Conceptually:

       address(values[i]) = EBP + base_offset + i * 4

9. local_size
   Record the total number of bytes reserved for local variables and
   arrays in each function.

10. Memory-layout information expected by neo.py
    The supplied GUI expects the parser to expose:

        parser.memory_layouts

    as a dictionary indexed by function name. Each function entry
    must contain:

        local_size
        entries

    Each item in entries describes a parameter, variable or array
    using the fields needed by the GUI, including name, kind, type,
    offset and size_bytes. Array entries also include size.

    The global function symbol should retain its local_size and
    memory_layout information after the function scope is closed.

IMPORTANT CONCEPTUAL DISTINCTION
--------------------------------
The symbol table and the activation record are related but they are
not the same object.

The symbol table contains compile-time information about identifiers,
types, scopes and storage locations.

An activation record is created at runtime for each function call.
The evaluator supplied in this package continues to model runtime
activation records independently of the compile-time memory layout.

PRACTICE 7 DOES NOT INCLUDE
---------------------------
- three-address code
- assembly-code generation
- pointers
- matrices
- dynamic arrays
- arrays as function parameters
- storage reuse/lifetime optimisation

These restrictions are intentional. The memory layout calculated in
Practice 7 prepares the compiler for direct AST-to-assembly code
generation in Practice 8.

MINIMUM TESTS
-------------
Test at least:

- int array declaration, assignment and access
- bool array declaration, assignment and access
- variable expression used as an array index
- bool used incorrectly as an array index
- assignment of the wrong element type
- indexing a scalar variable
- using an array as a scalar
- zero-size array declaration
- runtime out-of-bounds access
- function parameters with positive offsets
- local scalar variables with negative offsets
- arrays occupying contiguous storage
- local_size calculation
- a variable declared in a nested block
- shadowing: two declarations with the same name in different scopes
  must receive different storage locations

Run:
    python -m py_compile neo.py compiler/*.py
    python neo.py
