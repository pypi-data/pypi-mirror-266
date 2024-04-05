from repo_ast_builder.pycg.pycg import CallGraphGenerator


def is_class(namespace: str, project: CallGraphGenerator):
    return project.class_manager.get(namespace) is not None

def is_valid_child(namespace: str, project: CallGraphGenerator):
    return namespace in project.module_manager.internal
