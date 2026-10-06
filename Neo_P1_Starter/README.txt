NEO — PRACTICE 1 STARTER
Language Processors
========================

This package contains the starter code for Practice 1 of the Neo
Language Processors project.

The graphical environment, robot world, runtime and AST node classes
are already provided.

Your task in Practice 1 is to implement the lexical analyzer and the
syntax analyzer for the Neo P1 language using SLY.


REQUIREMENTS
------------

- Python 3.12
- SLY 0.5
- Tkinter


INSTALLATION
------------

It is recommended to use a Python virtual environment.

Create the environment:

    python3.12 -m venv neo

Activate it on macOS/Linux:

    source neo/bin/activate

Activate it on Windows:

    neo\Scripts\activate

Install SLY:

    pip install sly==0.5

Tkinter must also be available in your Python installation.


RUNNING NEO
-----------

From the Neo_P1_Starter directory, run:

    python neo.py

The Neo graphical environment will open.

Initially, pressing Run will display a message indicating that the
compiler components have not yet been implemented. This is the expected
behavior of the starter project.


PROJECT STRUCTURE
-----------------

Neo_P1_Starter/
|
|-- neo.py
|-- README.txt
|
`-- compiler/
    |-- __init__.py
    |-- ast_nodes.py
    |-- lexer.py
    `-- parser.py


PROVIDED FILES
--------------

neo.py

    Contains the Neo graphical environment, the robot world and the
    runtime required to execute a valid AST.

    DO NOT MODIFY THIS FILE.


compiler/ast_nodes.py

    Contains the AST node classes used in Practice 1:

        Program
        Move
        Turn

    DO NOT MODIFY THIS FILE.


FILES TO IMPLEMENT
------------------

compiler/lexer.py

    Implement the lexical analyzer for Neo P1 using SLY.

    The lexer must recognize all lexical elements required by the
    Neo P1 language and correctly report lexical errors.


compiler/parser.py

    Implement the syntax analyzer for Neo P1 using SLY.

    The parser must recognize valid Neo P1 programs and construct
    their Abstract Syntax Tree (AST) using the node classes provided
    in compiler/ast_nodes.py.


IMPORTANT
---------

Do not modify the interfaces provided by neo.py or ast_nodes.py.

The AST produced by your parser is the interface between your language
processor and the Neo execution environment.

A program will only be executed by Neo after the lexical and syntax
analysis phases have completed successfully.

Detailed language specifications, requirements, examples and submission
instructions are provided in the Practice 1 assignment.