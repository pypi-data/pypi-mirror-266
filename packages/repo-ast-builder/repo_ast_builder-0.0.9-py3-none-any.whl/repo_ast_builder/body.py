from typing import Optional

from repo_ast_builder.method_name import resolve_method_name
from repo_ast_builder.namespace import is_class
from repo_ast_builder.pycg.machinery.modules import Module
from repo_ast_builder.pycg.pycg import CallGraphGenerator


def is_direct_descendant(scope: str, namespace: str):
    return scope.startswith(namespace) and scope.count(".") - 1 == namespace.count(".")


def resolve_body(namespace: str, project: CallGraphGenerator, parent_scope: Optional[Module] = None):
    scope = project.module_manager.internal.get(namespace)
    if scope is None and parent_scope is not None:
        scope = parent_scope

    child_scopes = list(scope.methods.keys())[1:] if scope is not None else []
    child_bodies = [resolve_body(child_scope, project, scope) for child_scope in child_scopes if
                    is_direct_descendant(child_scope, namespace)]

    call_namespaces = project.cg.get()[namespace] if namespace in project.cg.get() else []
    call_bodies = [{
        "type": "call",
        "method_name": resolve_method_name(namespace, project)
    } for namespace in call_namespaces if resolve_method_name(namespace, project) is not None]

    arguments = project.def_manager.get(namespace).points_to["name"].args
    typ = "class" if is_class(namespace, project) else "def"

    return {
        "method_name": resolve_method_name(namespace, project),
        "type": typ,
        "body": child_bodies + call_bodies,
        "arguments": list(arguments.keys())
    }
