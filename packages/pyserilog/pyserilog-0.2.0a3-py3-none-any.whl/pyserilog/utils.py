def full_name(class_type: type):
    if not isinstance(class_type, type):
        class_type = type(class_type)
    module = class_type.__module__
    if module == "__builtin__" or module == 'builtins':
        return class_type.__qualname__
    return f'{module}.{class_type.__qualname__}'
