import json
import os
from pathlib import Path
from .pycg.pycg import CallGraphGenerator


def walk_repository(directory: Path) -> dict:
    entries = [str(path) for path in directory.rglob("*.py") if not "/." in str(path) and not "pylint/tests" in str(path)]
    finished = False

    while not finished:
        try:
            gen = CallGraphGenerator(entries, str(directory).split(os.sep)[-1], -1, "call-graph")
            gen.analyze()
            finished = True
        except SyntaxError as e:
            entries.remove(e.filename)
            print("Rerunning while excluding " + e.filename)


    repository_info = {}

    def is_class(namespace: str):
        return gen.class_manager.get(namespace) is not None

    def is_def(namespace: str):
        return namespace in gen.cg.get()

    def is_valid_child(namespace: str):
        return is_class(namespace) or is_def(namespace)

    def resolve_method_name(namespace: str):
        filepath = None
        find_namespace = namespace
        while '.' in find_namespace and filepath is None:
            filepath = gen.import_manager.get_filepath(find_namespace)
            find_namespace = ".".join(find_namespace.split(".")[:-1])
        return {
            "file": filepath,
            "namespace": namespace
        }

    def resolve_body(namespace: str):

        scope = gen.scope_manager.get_scope(namespace)

        child_scopes = list(scope.defs.values())[1:] if scope is not None else []
        child_bodies = [resolve_body(m.fullns) for m in child_scopes if is_valid_child(m.fullns)]

        call_namespaces = gen.cg.get()[namespace] if namespace in gen.cg.get() else []
        call_bodies = [{
            "type": "call",
            "method_name": resolve_method_name(namespace)
        } for namespace in call_namespaces if is_valid_child(namespace)]

        arguments = gen.def_manager.get(namespace).points_to["name"].args
        typ = "class" if is_class(namespace) else "def"

        return {
            "method_name": resolve_method_name(namespace),
            "type": typ,
            "body": child_bodies + call_bodies,
            "arguments": list(arguments.keys())
        }

    internal_modules = gen.module_manager.get_internal_modules().items()
    for module_name, module in internal_modules:
        repository_info[module.filename] = resolve_body(module_name)["body"]
        #imports = gen.import_manager.get_imports(module_name)

    return repository_info


if __name__ == "__main__":
    directory = Path("/Users/manuel/PycharmProjects/LLMLingua")
    with open("/Users/manuel/PycharmProjects/ast-walker/repository_info.json", "w") as f:
        f.write(json.dumps(walk_repository(directory)))
