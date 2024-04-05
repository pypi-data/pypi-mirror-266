# Repo AST Builder

## Purpose
This application creates an AST of a Python project, which can be used to get _overview_ of the project.

## Usage
```
from repo_ast_builder import read_ast

directory = "../repository"
output = read_ast(directory)
print(output)

```