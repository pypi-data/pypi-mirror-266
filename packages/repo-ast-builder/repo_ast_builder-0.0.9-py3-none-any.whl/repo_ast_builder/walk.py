import os
from pathlib import Path

from repo_ast_builder.body import resolve_body
from repo_ast_builder.pycg.pycg import CallGraphGenerator
from repo_ast_builder.pycg.utils.constants import CALL_GRAPH_OP


def walk_repository(directory: Path) -> dict:
    project: CallGraphGenerator
    os.chdir(directory)
    entries = [
        str(path)[len(str(directory))+1:]
        for path in directory.rglob("*.py")
        if not "/." in str(path)
    ]
    analyzation_complete = False

    while not analyzation_complete:
        try:
            project = CallGraphGenerator(entries, "", -1, CALL_GRAPH_OP)
            project.analyze()
            analyzation_complete = True
        except SyntaxError as e:
            entries.remove(e.filename)
            print(f"Syntax error in file '{e.filename}'. Excluding and rerunning..")

    repository_info = {}

    internal_modules = project.module_manager.get_internal_modules().items()
    for module_name, module in internal_modules:
        repository_info[module.filename] = resolve_body(module_name, project)["body"]
        # imports = project.import_manager.get_imports(module_name)

    return repository_info
