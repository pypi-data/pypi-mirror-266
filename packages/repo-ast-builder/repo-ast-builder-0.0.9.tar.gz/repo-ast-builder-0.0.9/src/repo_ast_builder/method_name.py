from repo_ast_builder.pycg.pycg import CallGraphGenerator


def resolve_method_name(namespace: str, project: CallGraphGenerator):
    #final = resolve_method_name2(namespace, project)
    #print()
    for module_name, module in project.module_manager.internal.items():
        if namespace in module.methods:
            return {
                "namespace": namespace,
                "file": module.filename,
            }
    for module_name, module in project.module_manager.external.items():
        if namespace in module.methods:
            return None
    return {
        "namespace": namespace,
        "file": None,
    }

def resolve_method_name2(namespace: str, project: CallGraphGenerator):
    for module_name, module in project.module_manager.internal.items():
        if namespace in module.methods:
            return {
                "namespace": namespace,
                "file": module.filename,
            }
    return {
        "namespace": namespace,
        "file": None,
    }
