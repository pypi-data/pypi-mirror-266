from importlib import metadata


def find_plugins(ignore=None):
    ignore = ignore or set()
    result = []
    for ep in metadata.entry_points(group='dekshell.plugins'):
        if ep.name not in ignore:
            data = ep.load()
            result.append({'name': ep.name, 'module': ep.module, **data})
    return result


def get_markers_from_modules(**kwargs):
    return get_attr_from_modules('markers', **kwargs)


def get_contexts_from_modules(**kwargs):
    return get_attr_from_modules('contexts', **kwargs)


def get_attr_from_modules(attr_name, **kwargs):
    result = []
    for plugin in find_plugins(**kwargs):
        result.extend(plugin.get(attr_name) or [])
    return result
