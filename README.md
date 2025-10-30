# Mini Compiler Project

A lightweight compiler for a C-like language written in Python, using the PLY (Python Lex-Yacc) library.  
Supports variables, arithmetic, arrays, loops, conditionals, floating-point, and functions.  
Designed for CSE 430 Compiler Design Lab, University of Asia Pacific.

## Features

- Lexical analysis (tokenizes keywords, identifiers, numbers, operators, etc.)
- Syntax parsing with context-free grammar (supports assignment, expressions, if-else, while, function definition/call)
- Symbol table management (handles nested scope and arrays)
- Intermediate code generation (Three Address Code / TAC)
- Error detection for syntax and semantic issues (undeclared variables, misuse of arrays, etc.)
- Easily extensible for more language features

## Getting Started

1. **Clone the repository:**
    ```
    git clone https://github.com/bitto03/compiler.git
    ```
2. **Install dependencies:**
    ```
    pip install ply
    ```
3. **Run the compiler:**
    ```
    python mini_compiler.py
    ```

4. **Testing:**
    - You may edit `test_code` string inside `mini_compiler.py` or provide input via file.

## Usage

Include your source code as a Python string, and the compiler will output:
- The token stream
- Parsed results and diagnostic errors
- Symbol table state
- Three-address code for the whole program

