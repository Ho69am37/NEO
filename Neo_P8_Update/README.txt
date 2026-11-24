NEO - PRACTICE 8 UPDATE
Code Generation

This package updates your existing Neo project from Practice 7.

HOW TO USE THIS PACKAGE
-----------------------
Copy these files into your existing Neo P7 project.

FILES PROVIDED
--------------
neo.py
    Updated Neo GUI integration for Practice 8.
    After lexical, syntactic and semantic analysis, it displays:
        - AST
        - Symbol Table
        - Memory Layout
        - generated Assembly
    The supplied evaluator still executes the AST so that you can
    observe the robot behaviour.

compiler/ast_nodes.py
    AST node definitions used by Neo.

compiler/evaluator.py
    Runtime/evaluation support used to execute the AST and control
    the virtual robot.

compiler/code_generator.py
    NEW in Practice 8.
    A partially implemented backend skeleton. You must complete the
    AST-to-assembly translation.

FILES YOU KEEP FROM YOUR OWN P7 PROJECT
---------------------------------------
compiler/lexer.py
compiler/parser.py
compiler/symbol_table.py

Do NOT replace these with a new compiler. Practice 8 builds on the
processor that you developed in Practices 1-7.

YOUR TASK
---------
Complete compiler/code_generator.py so that Neo generates pedagogical
32-bit x86 assembly in AT&T syntax directly from the AST.

There is NO three-address-code phase:

    Neo source
        -> lexer
        -> parser + semantic actions
        -> AST
        -> code generator
        -> assembly

The AST is the intermediate representation used by this practice.

CODE-GENERATION CONVENTIONS
---------------------------
1. Expression result
   Every expression leaves its result in:

       %eax

2. Boolean representation

       false = 0
       true  = 1

3. Function frame

       pushl %ebp
       movl %esp, %ebp
       subl $local_size, %esp     # only when local_size > 0

   Parameters use positive offsets and local storage uses the negative
   offsets calculated in Practice 7.

4. Function calls
   Use a simplified cdecl-style convention:
   - arguments are pushed right-to-left;
   - first parameter is at 8(%ebp);
   - caller removes arguments after the call;
   - non-void return value is in %eax.

5. Signed integer division
   Use signed division:

       cdq
       idivl <divisor>

6. Arrays
   int and bool elements occupy 4 bytes.

       address(a[i]) = EBP + base_offset + i * 4

   Use the base offset computed in Practice 7.

7. Control flow
   Generate labels and conditional/unconditional jumps for:
   - if
   - if/else
   - while
   - !
   - && and ||

   && and || MUST preserve short-circuit evaluation.

8. Neo runtime primitives
   Generate calls using these conventions:

       move(expression)
           expression result in %eax
           call neo_move

       turn(LEFT)
           movl $0, %eax
           call neo_turn

       turn(RIGHT)
           movl $1, %eax
           call neo_turn

       obstacle()
           call neo_obstacle
           result in %eax

       goal()
           call neo_goal
           result in %eax

WHAT YOU MUST IMPLEMENT
-----------------------
Complete these methods in compiler/code_generator.py:

    _generate_statement()
    _generate_expression()
    _generate_call()

The supplied infrastructure already provides:
- assembly-line emission;
- unique-label generation;
- function prologue setup;
- use of Practice-7 local_size;
- lexical-scope reconstruction;
- association between AST declarations and memory-layout entries.

Your implementation must support all Neo features developed so far:
- int and bool values;
- scalar variables;
- arithmetic expressions;
- comparisons;
- boolean expressions;
- assignments;
- if / else;
- while;
- functions, parameters and return;
- recursion;
- static one-dimensional arrays;
- move, turn, obstacle and goal.

IMPORTANT
---------
The generated assembly is an educational representation of the
backend and is displayed by Neo. It is not assembled or executed
natively.

The virtual robot continues to be executed by the supplied AST
evaluator. This allows the generated code and the observable program
behaviour to be inspected together.

Do not implement:
- three-address code;
- an additional intermediate representation;
- optimisation;
- register allocation;
- native assembly execution;
- pointers;
- matrices;
- dynamic arrays;
- arrays as parameters.

MINIMUM TESTS
-------------
Test code generation progressively. At minimum include:

- integer and boolean constants;
- scalar variable load/store;
- +, -, *, signed /;
- comparisons;
- unary - and !;
- short-circuit && and ||;
- if and if/else;
- while;
- move and turn;
- obstacle() and goal();
- a function with one parameter and return value;
- a function with two parameters;
- a recursive function;
- array assignment and access;
- an array indexed by a variable;
- a program combining functions, arrays, control flow and sensors.

CHECKING THE PROJECT
--------------------
Run:

    python -m py_compile neo.py compiler/*.py
    python neo.py

The final Neo console should show the analysis results, memory layout,
generated assembly and the execution of the program.
