from pyserilog.guard import Guard


def is_valid_name(name: str):
    return name is not None and len(name) > 0


def ensure_valid_name(name: str):
    Guard.against_null(name)
    if not is_valid_name(name):
        raise Exception("Property name must not be empty or whitespace.")
